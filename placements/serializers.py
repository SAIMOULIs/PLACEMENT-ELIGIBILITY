from rest_framework import serializers
from .models import Student, Company, Shortlist, UploadBatch, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'first_name', 'last_name']


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class CompanySerializer(serializers.ModelSerializer):
    shortlist_count = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = '__all__'
        read_only_fields = ['created_at', 'created_by']

    def get_shortlist_count(self, obj):
        return obj.shortlists.count()


class ShortlistSerializer(serializers.ModelSerializer):
    student_name  = serializers.CharField(source='student.name', read_only=True)
    student_roll  = serializers.CharField(source='student.roll_number', read_only=True)
    student_cgpa  = serializers.DecimalField(source='student.cgpa', max_digits=4, decimal_places=2, read_only=True)
    student_branch = serializers.CharField(source='student.branch', read_only=True)
    company_name  = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = Shortlist
        fields = '__all__'


class UploadBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadBatch
        fields = '__all__'
        read_only_fields = ['upload_time', 'uploaded_by', 'status',
                            'total_records', 'success_records', 'failed_records']
