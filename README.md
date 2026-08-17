# 🎓 PlaceTrack — Placement Eligibility & Auto-Shortlisting System

---

A full-stack Placement Management Platform built using **Python, Django, Django REST Framework, PostgreSQL/MySQL, JWT Authentication, and Excel Processing Automation**.

The system automates the entire placement eligibility verification and candidate shortlisting process, eliminating manual Excel filtering and reducing placement officer workload.

🌐 **Live Demo:** https://placement-eligibility-ivf2.onrender.com/

---

# 🚀 Problem Statement

In many colleges, placement officers manually verify student eligibility for every company.

The traditional process involves:

- Collecting student records in Excel sheets
- Verifying CGPA criteria manually
- Checking active backlogs
- Filtering branch eligibility
- Creating shortlist sheets manually
- Repeating the process for every company

This process is:

❌ Time-consuming

❌ Error-prone

❌ Difficult to scale

❌ Dependent on manual effort

---

# 💡 Solution

PlaceTrack automates the complete eligibility verification workflow.

Placement officers can:

- Upload student records
- Configure company eligibility rules
- Automatically generate eligible candidates
- Create instant shortlists
- Track placement statistics
- Manage multiple companies from one dashboard

The platform performs rule-based eligibility verification within seconds.

---

# ✨ Key Features

### 🔐 Role-Based Authentication

- Admin Login
- Placement Officer Login
- JWT Authentication
- Protected Routes

### 📊 Placement Dashboard

- Student Statistics
- Company Statistics
- Shortlisted Candidates
- Placement Analytics

### 🏢 Company Management

- Add Companies
- Define Eligibility Rules
- Package Tracking
- Branch Eligibility

### 📄 Student Data Processing

- CSV Upload
- Excel Upload
- Bulk Student Import
- Data Validation

### ⚡ Auto Shortlisting Engine

Automatically verifies:

- CGPA Criteria
- Backlog Criteria
- Branch Eligibility
- Academic Conditions

### 📈 Reporting

- Eligible Students
- Shortlisted Students
- Company Wise Reports
- Placement Summary

---

# 🏗 System Architecture

Student Dataset
↓
Data Upload Module
↓
Database Storage
↓
Eligibility Engine
↓
Shortlisting Module
↓
Dashboard & Reports

---

# 🛠 Tech Stack

## Backend

- Python 3.12
- Django 4.2
- Django REST Framework

## Database

- PostgreSQL (Production)
- MySQL (Development)

## Authentication

- JWT Authentication
- Django Authentication System

## Frontend

- HTML5
- CSS3
- JavaScript
- Django Templates

## File Processing

- OpenPyXL
- CSV Processing

## Deployment

- Render
- GitHub

## Version Control

- Git
- GitHub

---

# 📂 Project Structure

```text
PLACEMENT-ELIGIBILITY/
│
├── placement_system/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── placements/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── serializers.py
│   ├── templates/
│   └── static/
│
├── requirements.txt
├── build.sh
├── render.yaml
└── manage.py
```

# 🔄 Workflow

### Step 1

Placement Officer logs into the platform.

### Step 2

Student records are uploaded through CSV/Excel.

### Step 3

Company eligibility criteria are configured.

### Step 4

System validates all student records.

### Step 5

Eligibility Engine applies rules automatically.

### Step 6

Shortlisted candidates are generated instantly.

### Step 7

Reports are displayed on dashboard.

---

# 📊 Impact

### Before Automation

- Manual Excel Filtering
- Human Errors
- Long Processing Time

### After Automation

✅ Faster Processing

✅ Accurate Eligibility Verification

✅ Reduced Manual Work

✅ Scalable Placement Operations

---

# 🔒 Security Features

- JWT Authentication
- Session Management
- Protected APIs
- Role-Based Access Control
- Secure Password Storage

---

# 🌍 Deployment

Production Deployment:

https://placement-eligibility-ivf2.onrender.com/

Repository:

https://github.com/SAIMOULIs/PLACEMENT-ELIGIBILITY

---

# 👨‍💻 Author

**Bonu Sai Chandra Mouli**

B.Tech Computer Science & Engineering

Python Developer | Django Developer | Backend Engineer

GitHub:
https://github.com/SAIMOULIs

Portfolio:
https://saimoulis.github.io/PORTFOLIO/

---

# ⭐ Future Enhancements

- AI-Based Placement Prediction
- Resume Parsing
- Email Notifications
- Student Portal
- Analytics Dashboard
- Multi-College Support
- Company Portal
- Interview Scheduling
