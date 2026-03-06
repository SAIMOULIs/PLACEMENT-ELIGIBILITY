# 🎓 PlaceTrack — Placement Eligibility & Auto-Shortlisting System

A full-stack **Django REST Framework + MySQL + HTML/CSS** backend automation platform for college placement management.

---

## 🛠 Tech Stack
- **Backend**: Python 3.10+, Django 4.2, Django REST Framework
- **Database**: MySQL 8.0
- **Auth**: JWT (djangorestframework-simplejwt)
- **Frontend**: Django Templates + HTML/CSS (custom design system)
- **File Upload**: CSV and Excel (.xlsx) processing via openpyxl

---

## ⚙️ Setup Instructions (WSL / Ubuntu / Linux)

### Step 1 — Install Python packages
```bash
pip install -r requirements.txt
```

### Step 2 — Create MySQL Database
Open MySQL shell:
```sql
CREATE DATABASE placement_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'placement_user'@'localhost' IDENTIFIED BY 'yourpassword';
GRANT ALL PRIVILEGES ON placement_db.* TO 'placement_user'@'localhost';
FLUSH PRIVILEGES;
```

### Step 3 — Update settings.py
Edit `placement_system/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'placement_db',
        'USER': 'root',         # or 'placement_user'
        'PASSWORD': 'yourpassword',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

### Step 4 — Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5 — Create Admin User
```bash
python manage.py createsuperuser
```
When prompted, also set `role = admin` via Django Admin or shell:
```python
python manage.py shell
>>> from placements.models import User
>>> u = User.objects.get(username='admin')
>>> u.role = 'admin'
>>> u.save()
```

### Step 6 — Run the Server
```bash
python manage.py runserver
```

Open browser: **http://127.0.0.1:8000/**

---

## 🌐 Pages & URLs

| URL | Description |
|-----|-------------|
| `/` | Login page |
| `/dashboard/` | Analytics dashboard |
| `/students/` | Student list with filters |
| `/companies/` | Company drive cards |
| `/companies/<id>/` | Company detail + shortlist |
| `/shortlists/` | All shortlists with export |
| `/upload/` | Bulk CSV/Excel upload |
| `/admin/` | Django admin panel |
| `/api/` | REST API browser |

---

## 🔌 REST API Endpoints

### Auth
```
POST /api/token/          # Get JWT token
POST /api/token/refresh/  # Refresh JWT
```

### Students
```
GET    /api/students/              # List (filter: ?branch=CSE&min_cgpa=7&year=2025)
POST   /api/students/              # Create one student
POST   /api/students/upload/       # Bulk CSV/Excel upload
GET    /api/students/{id}/         # Get student
PUT    /api/students/{id}/         # Update student
DELETE /api/students/{id}/         # Delete student
```

### Companies
```
GET    /api/companies/                          # List
POST   /api/companies/                          # Create
POST   /api/companies/{id}/generate_shortlist/  # ⚡ Run eligibility engine
GET    /api/companies/{id}/shortlist/           # View company shortlist
```

### Shortlists
```
GET  /api/shortlists/         # List (filter: ?company=1&status=shortlisted)
GET  /api/shortlists/export/  # Download CSV (filter: ?company=1)
```

### Dashboard
```
GET  /api/dashboard/  # Analytics stats
```

---

## 🔐 Role-Based Access

| Role | Capabilities |
|------|-------------|
| **admin** | Full access, user management |
| **officer** | Upload students, manage companies, generate shortlists |
| **company** | View their own shortlist |
| **student** | View own profile |

---

## ⚡ Using the API with JWT

1. Get token:
```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "yourpassword"}'
```

2. Store in browser console (for HTML frontend buttons):
```javascript
sessionStorage.setItem('jwt', 'YOUR_ACCESS_TOKEN_HERE')
```

3. Use in API calls:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://127.0.0.1:8000/api/dashboard/
```

---

## 📤 CSV Upload Format

| Column | Required | Example |
|--------|----------|---------|
| name | ✅ | Ravi Kumar |
| roll_number | ✅ | 22CS001 |
| email | ✅ | ravi@college.edu |
| cgpa | ✅ | 8.5 |
| backlogs | No | 0 |
| branch | ✅ | CSE |
| skills | No | Python,Django,SQL |
| graduation_year | ✅ | 2025 |
| phone | No | 9876543210 |

Download sample CSV from the Upload page.

---

## 🗂 Project Structure

```
placement_system/
├── manage.py
├── requirements.txt
├── README.md
│
├── placement_system/          # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
└── placements/                # Main app
    ├── models.py              # DB tables (Student, Company, Shortlist, ...)
    ├── serializers.py         # DRF serializers
    ├── views.py               # API ViewSets
    ├── web_views.py           # HTML template views
    ├── urls.py                # API URL routes
    ├── web_urls.py            # HTML URL routes
    ├── permissions.py         # Role-based permissions
    ├── admin.py               # Django admin config
    ├── apps.py
    │
    ├── services/
    │   └── eligibility_engine.py   # Core rule engine
    │
    └── templates/
        └── placements/
            ├── base.html           # Layout + CSS design system
            ├── login.html
            ├── dashboard.html
            ├── students.html
            ├── companies.html
            ├── company_detail.html
            ├── shortlists.html
            └── upload.html
```

---

## 💼 Resume Description

> Designed and implemented a scalable **Placement Eligibility & Auto-Shortlisting System** using Django REST Framework and MySQL, featuring bulk CSV/Excel data ingestion, a dynamic multi-rule eligibility engine, JWT-based role authentication, REST API with pagination/filtering, and an interactive HTML/CSS dashboard.
