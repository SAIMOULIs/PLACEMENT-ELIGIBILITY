from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Count, Avg, Q
from .models import User, Student, Company, Shortlist, UploadBatch, SystemLog


def landing_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'placements/landing.html')


def demo_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    demo_companies = [
        {'name': 'TechNova Solutions', 'package': '8.5 LPA', 'eligible': 186, 'shortlisted': 42, 'rule': 'CGPA ≥ 7.0 · ≤ 2 backlogs'},
        {'name': 'CloudSphere Labs', 'package': '10.0 LPA', 'eligible': 142, 'shortlisted': 35, 'rule': 'CGPA ≥ 7.5 · CSE/IT'},
        {'name': 'DataForge Systems', 'package': '7.2 LPA', 'eligible': 211, 'shortlisted': 50, 'rule': 'CGPA ≥ 6.5 · Python/SQL'},
    ]
    return render(request, 'placements/demo.html', {
        'stats': {'students': 500, 'companies': 12, 'shortlisted': 127, 'avg_cgpa': '7.84'},
        'demo_companies': demo_companies,
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    error = None
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username', '').strip(),
            password=request.POST.get('password', ''),
        )
        if user:
            auth_login(request, user)
            return redirect('dashboard')
        error = 'Invalid username or password, or your account is awaiting approval.'
    return render(request, 'placements/login.html', {'error': error})


def signup_view(request):
    """Create a Student account or an inactive Placement Officer account."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        role = request.POST.get('role', 'student')

        if not username or not email or not password:
            error = 'Please complete all required fields.'
        elif len(username) < 3:
            error = 'Username must contain at least 3 characters.'
        elif len(password) < 8:
            error = 'Password must contain at least 8 characters.'
        elif password != confirm_password:
            error = 'Passwords do not match.'
        elif User.objects.filter(username__iexact=username).exists():
            error = 'That username is already in use.'
        elif User.objects.filter(email__iexact=email).exists():
            error = 'That email address is already registered.'
        elif role not in {'student', 'placement_officer'}:
            error = 'Please select a valid account type.'
        else:
            try:
                # IMPORTANT: this project uses placements.User as AUTH_USER_MODEL.
                # Do not import django.contrib.auth.models.User here.
                user_role = 'officer' if role == 'placement_officer' else 'student'
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    role=user_role,
                )

                if role == 'placement_officer':
                    # Officer accounts require administrator approval.
                    user.is_active = False
                    user.save(update_fields=['is_active'])
                    return render(request, 'placements/signup_pending.html')

                # Students can use the application immediately.
                auth_login(request, user)
                messages.success(request, 'Your PlaceTrack account has been created successfully.')
                return redirect('dashboard')
            except IntegrityError:
                error = 'Unable to create the account. Please check your details and try again.'

    return render(request, 'placements/signup.html', {'error': error})


def logout_view(request):
    auth_logout(request)
    return redirect('landing')


def _is_placement_officer(user):
    return user.is_superuser or user.is_staff or user.role == 'officer'


@login_required
def dashboard(request):
    if not _is_placement_officer(request.user):
        return render(request, 'placements/student_dashboard.html', {
            'username': request.user.get_full_name() or request.user.username
        })

    ctx = {
        'total_students': Student.objects.count(),
        'total_companies': Company.objects.count(),
        'total_shortlists': Shortlist.objects.count(),
        'total_batches': UploadBatch.objects.count(),
        'avg_cgpa': Student.objects.aggregate(avg=Avg('cgpa'))['avg'],
        'branch_dist': Student.objects.values('branch').annotate(count=Count('id')).order_by('-count'),
        'recent_companies': Company.objects.annotate(shortlisted=Count('shortlists')).order_by('-created_at')[:5],
        'recent_logs': SystemLog.objects.all()[:8],
    }
    return render(request, 'placements/dashboard.html', ctx)


@login_required
def students_list(request):
    if not _is_placement_officer(request.user):
        return redirect('dashboard')
    qs = Student.objects.all()
    branch = request.GET.get('branch', '')
    year = request.GET.get('year', '')
    search = request.GET.get('search', '')
    if branch:
        qs = qs.filter(branch=branch)
    if year:
        qs = qs.filter(graduation_year=year)
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(roll_number__icontains=search))
    return render(request, 'placements/students.html', {
        'students': qs[:200],
        'branch': branch,
        'year': year,
        'search': search,
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
    if not _is_placement_officer(request.user):
        return redirect('dashboard')
    companies = Company.objects.annotate(shortlisted=Count('shortlists')).order_by('-created_at')
    return render(request, 'placements/companies.html', {'companies': _add_branches(companies)})


@login_required
def company_detail(request, pk):
    if not _is_placement_officer(request.user):
        return redirect('dashboard')
    company = get_object_or_404(Company, pk=pk)
    shortlists = Shortlist.objects.filter(company=company).select_related('student')
    company.branches_display = [b.strip() for b in company.eligible_branches.split(',') if b.strip()]
    return render(request, 'placements/company_detail.html', {'company': company, 'shortlists': shortlists})


@login_required
def shortlists_view(request):
    if not _is_placement_officer(request.user):
        return redirect('dashboard')
    shortlists = Shortlist.objects.select_related('student', 'company').all()
    company_id = request.GET.get('company', '')
    if company_id:
        shortlists = shortlists.filter(company_id=company_id)
    return render(request, 'placements/shortlists.html', {
        'shortlists': shortlists[:300],
        'companies': Company.objects.all(),
        'selected_company': company_id,
    })


@login_required
def upload_view(request):
    if not _is_placement_officer(request.user):
        return redirect('dashboard')
    return render(request, 'placements/upload.html', {'batches': UploadBatch.objects.all()})
