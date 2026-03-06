from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Student, Company, Shortlist, UploadBatch, SystemLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ['username', 'email', 'role', 'is_active']
    list_filter   = ['role', 'is_active']
    fieldsets     = BaseUserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
    )


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display  = ['roll_number', 'name', 'branch', 'cgpa', 'backlogs', 'graduation_year']
    list_filter   = ['branch', 'graduation_year']
    search_fields = ['name', 'roll_number', 'email']


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display  = ['name', 'min_cgpa', 'max_backlogs', 'package', 'deadline']
    search_fields = ['name']


@admin.register(Shortlist)
class ShortlistAdmin(admin.ModelAdmin):
    list_display  = ['student', 'company', 'status', 'shortlisted_at']
    list_filter   = ['status', 'company']


@admin.register(UploadBatch)
class UploadBatchAdmin(admin.ModelAdmin):
    list_display  = ['file_name', 'uploaded_by', 'upload_time', 'total_records', 'status']


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display  = ['log_type', 'message', 'user', 'created_at']
    list_filter   = ['log_type']
