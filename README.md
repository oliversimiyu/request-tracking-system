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

## Admin test credentials 

Username admin
password admin123

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

### Authentication
- `POST /login/` - Admin login (returns session cookie)
- `POST /logout/` - Admin logout
- `GET /api/auth/` - DRF authentication endpoints

### Public Endpoints (No Authentication Required)
- `POST /api/public/submit-request/` - Submit new service request
- `GET /api/public/request-status/{id}/` - Check request status by ID

### Service Requests API (Authenticated Users)
- `GET /api/requests/` - List all service requests with filtering
- Query params: `?status=pending&category=hardware&department=IT&search=printer`
- `GET /api/requests/{id}/` - Get service request details
- `POST /api/requests/` - Create new service request (staff only)
- `PUT /api/requests/{id}/` - Update service request (staff only)
- `PATCH /api/requests/{id}/` - Partially update service request (staff only)
- `DELETE /api/requests/{id}/` - Delete service request (staff only)
- `POST /api/requests/{id}/update-status/` - Update request status (staff only)
- `GET /api/requests/stats/` - Get service request statistics (staff only)

### Departments API (Authenticated Users)
- `GET /api/departments/` - List all departments
- `GET /api/departments/{id}/` - Get department details
- `POST /api/departments/` - Create new department (staff only)
- `PUT /api/departments/{id}/` - Update department (staff only)
- `PATCH /api/departments/{id}/` - Partially update department (staff only)
- `DELETE /api/departments/{id}/` - Delete department (staff only)
- `POST /api/departments/sync-api/` - Sync departments from external API (staff only)
- `GET /api/departments/stats/` - Get department statistics (staff only)


### Web Interface Endpoints
- `GET /` - Homepage with service request form
- `GET /dashboard/` - Admin dashboard with statistics
- `GET /requests/` - List all requests (admin view)
- `GET /requests/{id}/` - Request detail view
- `POST /requests/{id}/update-status/` - AJAX status update
- `GET /status/{id}/` - Public status check page
- `GET /departments/` - Department management
- `POST /departments/add/` - Add new department
- `GET /departments/{id}/edit/` - Edit department
- `POST /departments/{id}/delete/` - Delete department
- `POST /departments/sync-api/` - Sync from external API

