# IT Service Request Tracking System

A Django web application for managing IT service requests with dashboard and status tracking.

**Live Demo**: https://request-tracking-system.onrender.com

## Features

- Submit IT service requests through web form
- Admin dashboard with statistics and charts
- Real-time status tracking (Pending → In Progress → Resolved → Closed)
- Request categories: Password Reset, Software Installation, Hardware Issues, etc.
- External API integration for department data

## Quick Setup

### Local Development

1. **Clone and setup**
   ```bash
   git clone https://github.com/oliversimiyu/request-tracking-system.git
   cd request-tracking-system
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install and run**
   ```bash
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

3. **Access application**
   - Main app: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/
   - Dashboard: http://127.0.0.1:8000/dashboard/

## Usage

### Submit Request (Staff)
1. Visit homepage
2. Fill out service request form
3. Select department and issue category
4. Submit request and note the ID for status checking

### Manage Requests (Admin)
1. Login via "Admin Login"
2. Access dashboard for overview and statistics
3. View/filter all requests
4. Update request status via dropdown

## Video demo

[![Watch the demo](https://img.youtube.com/vi/iJYr11Qi_yg/0.jpg)](https://youtu.be/iJYr11Qi_yg)

## Technology Stack

- **Backend**: Django 5.2.7, PostgreSQL
- **Frontend**: Bootstrap 5, Chart.js
- **Deployment**: Render with gunicorn
- **External API**: JSONPlaceholder for departments

## API Endpoints

- `POST /api/public/submit-request/` - Submit new request (public)
- `GET /api/public/request-status/{id}/` - Check status (public)
- `GET /api/requests/` - List requests (authenticated)
- `POST /api/requests/{id}/update-status/` - Update status (staff only)

Full API documentation: `/api-docs/`
