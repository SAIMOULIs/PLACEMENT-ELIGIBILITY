from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import OfficerAccessRequest, User
from . import web_views


def request_access(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm = request.POST.get('confirm_password', '')
        full_name = request.POST.get('full_name', '').strip()
        institution = request.POST.get('institution', '').strip()
        designation = request.POST.get('designation', '').strip()
        phone = request.POST.get('phone', '').strip()
        reason = request.POST.get('reason', '').strip()

        if not all([username, email, password, full_name, institution, designation]):
            error = 'Please complete all required fields.'
        elif len(username) < 3:
            error = 'Username must contain at least 3 characters.'
        elif len(password) < 8:
            error = 'Password must contain at least 8 characters.'
        elif password != confirm:
            error = 'Passwords do not match.'
        elif User.objects.filter(username__iexact=username).exists():
            error = 'That username is already in use.'
        elif User.objects.filter(email__iexact=email).exists():
            error = 'That email address is already registered.'
        else:
            try:
                # The account is intentionally inactive and has no officer role until approval.
                user = User.objects.create_user(
                    username=username, email=email, password=password,
                    role='student', is_active=False,
                )
                OfficerAccessRequest.objects.create(
                    user=user, full_name=full_name, institution=institution,
                    designation=designation, phone=phone, reason=reason,
                )
                return render(request, 'placements/officer_request_submitted.html', {'full_name': full_name})
            except IntegrityError:
                error = 'Unable to submit the request. Please check your details and try again.'

    return render(request, 'placements/officer_access_request.html', {'error': error})


def is_admin(user):
    return user.is_authenticated and user.is_superuser


@user_passes_test(is_admin)
def officer_requests(request):
    requests = OfficerAccessRequest.objects.select_related('user', 'reviewed_by').all()
    return render(request, 'placements/admin_officer_requests.html', {'requests': requests})


@user_passes_test(is_admin)
def approve_request(request, pk):
    access_request = get_object_or_404(OfficerAccessRequest, pk=pk)
    if request.method == 'POST' and access_request.status == 'pending':
        access_request.user.role = 'officer'
        access_request.user.is_active = True
        access_request.user.save(update_fields=['role', 'is_active'])
        access_request.status = 'approved'
        access_request.reviewed_at = timezone.now()
        access_request.reviewed_by = request.user
        access_request.review_notes = 'Approved by administrator.'
        access_request.save(update_fields=['status', 'reviewed_at', 'reviewed_by', 'review_notes'])
    return redirect('officer_requests')


@user_passes_test(is_admin)
def reject_request(request, pk):
    access_request = get_object_or_404(OfficerAccessRequest, pk=pk)
    if request.method == 'POST' and access_request.status == 'pending':
        access_request.user.is_active = False
        access_request.user.save(update_fields=['is_active'])
        access_request.status = 'rejected'
        access_request.reviewed_at = timezone.now()
        access_request.reviewed_by = request.user
        access_request.review_notes = 'Rejected by administrator.'
        access_request.save(update_fields=['status', 'reviewed_at', 'reviewed_by', 'review_notes'])
    return redirect('officer_requests')


@login_required
def dashboard_gate(request):
    user = request.user
    if not (user.is_superuser or user.is_staff or user.role == 'officer'):
        return render(request, 'placements/access_denied.html', {
            'message': 'This application is for authorized Placement Officers. Request access from the public site.'
        }, status=403)
    return web_views.dashboard(request)
