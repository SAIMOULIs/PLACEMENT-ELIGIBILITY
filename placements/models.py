from django.db import models
from django.contrib.auth.models import AbstractUser


# ── Custom User with roles ────────────────────────────────────────
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('officer', 'Placement Officer'),
        ('company', 'Company'),
        ('student', 'Student'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return f"{self.username} ({self.role})"


# ── Upload Batch (tracks CSV/Excel imports) ───────────────────────
class UploadBatch(models.Model):
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    file_name = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    upload_time = models.DateTimeField(auto_now_add=True)
    total_records = models.IntegerField(default=0)
    success_records = models.IntegerField(default=0)
    failed_records = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    error_log = models.TextField(blank=True)

    class Meta:
        db_table = 'upload_batch'
        ordering = ['-upload_time']

    def __str__(self):
        return f"{self.file_name} - {self.status}"


# ── Student ───────────────────────────────────────────────────────
class Student(models.Model):
    BRANCH_CHOICES = [
        ('CSE', 'Computer Science'),
        ('ECE', 'Electronics & Communication'),
        ('EEE', 'Electrical & Electronics'),
        ('ME',  'Mechanical Engineering'),
        ('CE',  'Civil Engineering'),
        ('IT',  'Information Technology'),
        ('AIDS', 'AI & Data Science'),
        ('CSBS', 'CS & Business Systems'),
        ('OTHER', 'Other'),
    ]
    name            = models.CharField(max_length=200)
    roll_number     = models.CharField(max_length=50, unique=True)
    email           = models.EmailField(unique=True)
    cgpa            = models.DecimalField(max_digits=4, decimal_places=2)
    backlogs        = models.IntegerField(default=0)
    branch          = models.CharField(max_length=10, choices=BRANCH_CHOICES)
    skills          = models.TextField(blank=True, help_text="Comma-separated skills")
    graduation_year = models.IntegerField()
    phone           = models.CharField(max_length=15, blank=True)
    upload_batch    = models.ForeignKey(UploadBatch, on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='students')
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student'
        ordering = ['-cgpa']

    def __str__(self):
        return f"{self.name} ({self.roll_number})"

    def skills_list(self):
        return [s.strip().lower() for s in self.skills.split(',') if s.strip()]


# ── Company ───────────────────────────────────────────────────────
class Company(models.Model):
    name              = models.CharField(max_length=200)
    description       = models.TextField(blank=True)
    min_cgpa          = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    max_backlogs      = models.IntegerField(default=0)
    eligible_branches = models.TextField(help_text="Comma-separated branch codes, e.g. CSE,IT,AIDS")
    required_skills   = models.TextField(blank=True, help_text="Comma-separated skills")
    eligible_year     = models.IntegerField(null=True, blank=True)
    package           = models.CharField(max_length=50, blank=True, help_text="e.g. 6 LPA")
    job_role          = models.CharField(max_length=200, blank=True)
    deadline          = models.DateField(null=True, blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)
    created_by        = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'company'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def branches_list(self):
        return [b.strip().upper() for b in self.eligible_branches.split(',') if b.strip()]

    def skills_list(self):
        return [s.strip().lower() for s in self.required_skills.split(',') if s.strip()]


# ── Shortlist ─────────────────────────────────────────────────────
class Shortlist(models.Model):
    STATUS_CHOICES = [
        ('shortlisted', 'Shortlisted'),
        ('selected', 'Selected'),
        ('rejected', 'Rejected'),
        ('pending', 'Pending'),
    ]
    student        = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='shortlists')
    company        = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='shortlists')
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='shortlisted')
    shortlisted_at = models.DateTimeField(auto_now_add=True)
    notes          = models.TextField(blank=True)

    class Meta:
        db_table = 'shortlist'
        unique_together = ('student', 'company')
        ordering = ['-shortlisted_at']

    def __str__(self):
        return f"{self.student.name} → {self.company.name}"


# ── System Log ────────────────────────────────────────────────────
class SystemLog(models.Model):
    LOG_TYPES = [
        ('upload', 'Upload'),
        ('shortlist', 'Shortlist Generation'),
        ('login', 'Login'),
        ('error', 'Error'),
    ]
    log_type   = models.CharField(max_length=20, choices=LOG_TYPES)
    message    = models.TextField()
    user       = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'system_log'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.log_type}] {self.message[:60]}"
