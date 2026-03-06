from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'students',  views.StudentViewSet,     basename='student')
router.register(r'companies', views.CompanyViewSet,     basename='company')
router.register(r'shortlists', views.ShortlistViewSet,  basename='shortlist')
router.register(r'batches',   views.UploadBatchViewSet, basename='batch')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', views.dashboard_stats, name='dashboard-stats'),
    path('register/',  views.register_user,   name='register-user'),
]
