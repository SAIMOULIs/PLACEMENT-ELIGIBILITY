from django.urls import path
from . import web_views

urlpatterns = [
    path('',            web_views.login_view,      name='login'),
    path('logout/',     web_views.logout_view,      name='logout'),
    path('dashboard/',  web_views.dashboard,        name='dashboard'),
    path('students/',   web_views.students_list,    name='students'),
    path('companies/',  web_views.companies_list,   name='companies'),
    path('companies/<int:pk>/', web_views.company_detail, name='company_detail'),
    path('shortlists/', web_views.shortlists_view,  name='shortlists'),
    path('upload/',     web_views.upload_view,      name='upload'),
]
