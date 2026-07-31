# ExpenseFlow

A modern, full-stack expense tracker built with **Django**, **Django REST Framework**, **Bootstrap 5**, and **Chart.js**. Track expenses, categorize spending, view analytics, generate reports, and manage your budget — all in a clean, premium UI with light/dark mode.

---

## ✨ Features

- **Authentication** — Register/login with email *or* phone number, "Remember Me", forgot/reset password flow
- **Dashboard** — Total balance, total/today/monthly expenses, top category, budget alerts, trend & category charts
- **Expense CRUD** — Add, edit, delete expenses with receipt upload, payment method, notes
- **Categories** — 15 default categories + unlimited custom categories with icons
- **Expense History** — Search, filter (date range/category/payment/amount), sort, pagination
- **Reports** — Daily/weekly/monthly/yearly reports, export to CSV, Excel, or PDF
- **Analytics** — Monthly trend, 30-day timeline, category & payment-method distribution, top categories, average/largest/smallest expense
- **Settings** — Currency (INR/USD/EUR), dark mode, monthly budget goal, password change
- **REST API** — Full JWT-authenticated API (`/api/`) for register, login, expenses, categories, analytics, reports — ready for a future mobile app
- **Docker-ready** — `Dockerfile`, `docker-compose.yml` (Postgres + Gunicorn + Nginx)

---

## 🧱 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Django 5, Django REST Framework, SimpleJWT |
| Frontend | Django Templates, Bootstrap 5, Bootstrap Icons, Chart.js, vanilla JS/AJAX |
| Database | SQLite (dev) / PostgreSQL (production) |
| Reports | ReportLab (PDF), Python `csv` (CSV/Excel) |
| Deployment | Gunicorn, Nginx, Docker, Whitenoise |

---

## 📁 Project Structure

```
expenseflow/
├── config/              # Django project settings, root urls, wsgi/asgi
├── users/               # Auth, Profile model, register/login/settings views
├── expenses/            # Category & Expense models, dashboard, CRUD, reports
├── analytics/           # Analytics dashboard (charts & stats)
├── api/                 # DRF REST API (JWT auth) + serializers/viewsets
├── templates/           # All HTML templates (Bootstrap 5)
├── static/               # CSS (design system) + JS (dark mode, AJAX, charts)
├── media/               # User-uploaded receipts & avatars (created at runtime)
├── nginx/nginx.conf     # Reverse proxy config for Docker deployment
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
├── requirements.txt
└── manage.py
```

---

## 🚀 Local Setup (SQLite, quickest way to run it)

> Requires Python 3.11+

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy environment variables
cp .env.example .env
# On Windows: copy .env.example .env

# 4. Run migrations
python manage.py makemigrations
python manage.py migrate

# 5. Seed the 15 default expense categories
python manage.py seed_categories

# 6. Create an admin account (optional, for /admin/)
python manage.py createsuperuser

# 7. Run the development server
python manage.py runserver
```

Then open **http://127.0.0.1:8000/** in your browser.

> **Note:** `.env` defaults to SQLite (`DB_ENGINE=sqlite`) and the console email backend (password-reset emails print to your terminal instead of sending real emails) — perfect for local development. Switch `DB_ENGINE=postgres` and fill in the `DB_*` variables to use PostgreSQL.

---

## 🐳 Running with Docker (PostgreSQL + Gunicorn + Nginx)

```bash
cp .env.example .env
# edit .env and set DB_ENGINE=postgres, a real SECRET_KEY, etc.

docker compose up --build
```

This starts three containers:
- `db` — PostgreSQL 16
- `web` — Django app served by Gunicorn (migrations + `seed_categories` + `collectstatic` run automatically via `entrypoint.sh`)
- `nginx` — reverse proxy on port 80, serving static/media files directly

Visit **http://localhost/**. Create a superuser inside the running container if needed:

```bash
docker compose exec web python manage.py createsuperuser
```

---

## 🔌 REST API

All endpoints are namespaced under `/api/` and use JWT auth (`Authorization: Bearer <token>`).

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/register/` | Create an account |
| POST | `/api/login/` | Obtain JWT access/refresh tokens (email or phone + password) |
| POST | `/api/token/refresh/` | Refresh an access token |
| GET/PUT | `/api/profile/` | View/update your profile |
| GET/POST | `/api/expenses/` | List / create expenses |
| GET/PUT/DELETE | `/api/expenses/{id}/` | Retrieve / update / delete an expense |
| GET/POST | `/api/categories/` | List / create categories |
| GET | `/api/analytics/` | Aggregated spending stats |
| GET | `/api/reports/?date_filter=this_month` | Filtered report data |

The Django admin site is available at `/admin/`.

---

## 🔐 Authentication Notes

- Users log in with **email or phone number** (a custom auth backend, `users.backends.EmailOrPhoneBackend`, checks both).
- Password reset uses Django's built-in token generator; in dev, reset links are printed to your terminal by the console email backend. Configure a real `EMAIL_BACKEND`/SMTP settings in `.env` for production.
- OTP-based verification was intentionally left out of this build to keep the auth flow simple and dependency-free — it can be added with a package like `django-otp` if you need it.

---

## ⚠️ Honest Limitations (things simplified for this build)

This was generated as a complete, runnable starting point rather than a fully audited production system. Before shipping to real users, you should:

- Review and harden `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, and CSRF/session cookie settings for production
- Add rate limiting to login/register/password-reset endpoints
- Add automated tests (none are included yet)
- Configure a real email backend (SMTP/SES/SendGrid) for password resets
- Review file upload validation (size/type limits) for receipts and avatars
- Add a Progressive Web App manifest/service worker if offline support is required — not included here
- This project was authored without a live Django environment to test against (no network access in the build sandbox). It follows standard Django 5 / DRF conventions carefully, but **please run `python manage.py check` and test the core flows (register → login → add expense → dashboard) immediately after setup** in case anything needs a small fix.

---

## 📄 License

Provided as-is for your own use and modification.
