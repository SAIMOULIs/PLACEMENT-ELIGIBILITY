from django.urls import path
from . import web_views, officer_access

urlpatterns = [
    path('', web_views.landing_view, name='landing'),
    path('demo/', web_views.demo_view, name='demo'),
    path('login/', web_views.login_view, name='login'),
    path('request-officer-access/', officer_access.request_access, name='officer_access_request'),
    path('signup/', officer_access.request_access, name='signup'),
    path('logout/', web_views.logout_view, name='logout'),
    path('dashboard/', officer_access.dashboard_gate, name='dashboard'),
    path('admin/officer-requests/', officer_access.officer_requests, name='officer_requests'),
    path('admin/officer-requests/<int:pk>/approve/', officer_access.approve_request, name='approve_officer_request'),
    path('admin/officer-requests/<int:pk>/reject/', officer_access.reject_request, name='reject_officer_request'),
    path('students/', web_views.students_list, name='students'),
    path('companies/', web_views.companies_list, name='companies'),
    path('companies/<int:pk>/', web_views.company_detail, name='company_detail'),
    path('shortlists/', web_views.shortlists_view, name='shortlists'),
    path('upload/', web_views.upload_view, name='upload'),
]
