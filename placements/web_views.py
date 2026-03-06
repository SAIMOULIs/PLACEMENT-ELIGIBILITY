from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from .models import Student, Company, Shortlist, UploadBatch, SystemLog


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    error = None
    if request.method == 'POST':
        user = authenticate(request,
                            username=request.POST['username'],
                            password=request.POST['password'])
        if user:
            auth_login(request, user)
            return redirect('dashboard')
        error = 'Invalid username or password.'
    return render(request, 'placements/login.html', {'error': error})


def logout_view(request):
    auth_logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    ctx = {
        'total_students':   Student.objects.count(),
        'total_companies':  Company.objects.count(),
        'total_shortlists': Shortlist.objects.count(),
        'total_batches':    UploadBatch.objects.count(),
        'avg_cgpa':         Student.objects.aggregate(avg=Avg('cgpa'))['avg'],
        'branch_dist':      Student.objects.values('branch').annotate(count=Count('id')).order_by('-count'),
        'recent_companies': Company.objects.annotate(shortlisted=Count('shortlists')).order_by('-created_at')[:5],
        'recent_logs':      SystemLog.objects.all()[:8],
    }
    return render(request, 'placements/dashboard.html', ctx)


@login_required
def students_list(request):
    qs     = Student.objects.all()
    branch = request.GET.get('branch', '')
    year   = request.GET.get('year', '')
    search = request.GET.get('search', '')
    if branch:
        qs = qs.filter(branch=branch)
    if year:
        qs = qs.filter(graduation_year=year)
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(roll_number__icontains=search))
    return render(request, 'placements/students.html', {
        'students': qs[:200],
        'branch':   branch,
        'year':     year,
        'search':   search,
        'branches': Student.BRANCH_CHOICES,
    })


def _add_branches(companies_qs):
    result = []
    for c in companies_qs:
        c.branches_display = [b.strip() for b in c.eligible_branches.split(',') if b.strip()]
        result.append(c)
    return result


@login_required
def companies_list(request):
    companies = Company.objects.annotate(shortlisted=Count('shortlists')).order_by('-created_at')
    return render(request, 'placements/companies.html', {
        'companies': _add_branches(companies),
    })


@login_required
def company_detail(request, pk):
    company    = get_object_or_404(Company, pk=pk)
    shortlists = Shortlist.objects.filter(company=company).select_related('student')
    company.branches_display = [b.strip() for b in company.eligible_branches.split(',') if b.strip()]
    return render(request, 'placements/company_detail.html', {
        'company': company, 'shortlists': shortlists,
    })


@login_required
def shortlists_view(request):
    shortlists = Shortlist.objects.select_related('student', 'company').all()
    company_id = request.GET.get('company', '')
    if company_id:
        shortlists = shortlists.filter(company_id=company_id)
    return render(request, 'placements/shortlists.html', {
        'shortlists':       shortlists[:300],
        'companies':        Company.objects.all(),
        'selected_company': company_id,
    })


@login_required
def upload_view(request):
    batches = UploadBatch.objects.all()
    return render(request, 'placements/upload.html', {'batches': batches})
