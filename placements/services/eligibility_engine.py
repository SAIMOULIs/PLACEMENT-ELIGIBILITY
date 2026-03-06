"""
Core Eligibility Rule Engine
Applies company-defined rules to filter eligible students.
"""
from placements.models import Student, Company, Shortlist, SystemLog


def run_eligibility_engine(company: Company, user=None) -> dict:
    """
    Apply all eligibility rules for a company and generate shortlist.
    Returns a summary dict.
    """
    # Start with all students
    qs = Student.objects.all()

    # Rule 1: CGPA filter
    qs = qs.filter(cgpa__gte=company.min_cgpa)

    # Rule 2: Backlog filter
    qs = qs.filter(backlogs__lte=company.max_backlogs)

    # Rule 3: Branch filter
    eligible_branches = company.branches_list()
    if eligible_branches:
        qs = qs.filter(branch__in=eligible_branches)

    # Rule 4: Graduation year filter
    if company.eligible_year:
        qs = qs.filter(graduation_year=company.eligible_year)

    students = list(qs)

    # Rule 5: Skills filter (done in Python for flexibility)
    required_skills = company.skills_list()
    if required_skills:
        matched = []
        for student in students:
            student_skills = student.skills_list()
            if any(skill in student_skills for skill in required_skills):
                matched.append(student)
        students = matched

    # Generate shortlist records
    created_count = 0
    skipped_count = 0
    for student in students:
        obj, created = Shortlist.objects.get_or_create(
            student=student,
            company=company,
            defaults={'status': 'shortlisted'}
        )
        if created:
            created_count += 1
        else:
            skipped_count += 1

    # Log the action
    SystemLog.objects.create(
        log_type='shortlist',
        message=f"Shortlist generated for {company.name}: "
                f"{len(students)} eligible, {created_count} new records.",
        user=user,
    )

    return {
        'company': company.name,
        'total_students_checked': Student.objects.count(),
        'eligible_students': len(students),
        'new_shortlist_records': created_count,
        'already_shortlisted': skipped_count,
        'rules_applied': {
            'min_cgpa': str(company.min_cgpa),
            'max_backlogs': company.max_backlogs,
            'eligible_branches': company.branches_list(),
            'required_skills': company.skills_list(),
            'eligible_year': company.eligible_year,
        }
    }
