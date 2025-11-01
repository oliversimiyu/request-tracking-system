# IT Service Request Tracking System

A Django-based web application for managing internal IT service requests, replacing email-based workflows with an automated web system.

## Features

### 🎯 Core Functionality
- **Service Request Submission**: Staff can submit IT requests through a web form
- **Request Management**: Admin/IT staff can view, filter, and manage all requests
- **Status Tracking**: Real-time status updates (Pending → In Progress → Resolved → Closed)
- **Dashboard**: Visual overview with statistics and charts

### 🔧 Technical Features
- **Database**: SQLite database storing all request data
- **Authentication**: Admin login system for IT staff
- **API Integration**: External API for dynamic department data
- **Automation**: Auto-status setting and assignment features
- **Responsive Design**: Bootstrap-powered responsive UI

### 🚀 Request Categories
- Password Reset
- Software Installation
- Hardware Issues
- Printer Issues
- Network Issues
- Account Access
- Other

## Technology Stack

- **Backend**: Django 5.2.7
- **Database**: SQLite
- **Frontend**: HTML5, Bootstrap 5.1.3, JavaScript
- **Charts**: Chart.js
- **Icons**: Font Awesome 6.0
- **API**: JSONPlaceholder (demo external API)

## Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd request-tracking-system
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install django requests python-decouple
   ```

4. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser account**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main application: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/
   - Dashboard: http://127.0.0.1:8000/dashboard/

## Usage Guide

### For End Users (Staff)

1. **Submit a Request**
   - Visit the home page
   - Fill out the service request form
   - Select your department (loaded dynamically via API)
   - Choose issue category and provide description
   - Submit the request

2. **Check Request Status**
   - Use the "Request Status" checker on the home page
   - Enter your request ID to view current status

### For IT Staff/Admins

1. **Login**
   - Click "Admin Login" in the navigation
   - Use your admin credentials

2. **View Dashboard**
   - Access overview of all requests
   - View statistics and charts
   - Quick access to recent requests

3. **Manage Requests**
   - View all requests with filtering options
   - Update request status via dropdown
   - View detailed request information
   - Use admin panel for advanced management

## System Architecture

### Database Schema

#### ServiceRequest Model
- `id`: Primary key (auto-generated)
- `requester_name`: Staff member name
- `department`: Department name
- `category`: Issue category
- `description`: Detailed description
- `status`: Current status (pending/in_progress/resolved/closed)
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update
- `assigned_to`: Assigned IT staff member (foreign key)

#### Department Model
- `id`: Primary key
- `name`: Department name
- `code`: Department code
- `manager`: Department manager
- `created_at`: Creation timestamp

### API Integration

The system integrates with external APIs for dynamic data:

- **Department Data**: Fetches department information from JSONPlaceholder API
- **Fallback**: Static department list if API is unavailable
- **Caching**: Departments stored in database after first API call

### Automation Features

1. **Default Status**: New requests automatically set to "Pending"
2. **Auto-Assignment**: Requests automatically assigned when status changes to "In Progress"
3. **Status Updates**: Real-time status updates via AJAX
4. **Timestamps**: Automatic tracking of creation and update times

## Configuration

### Environment Variables
Create a `.env` file for production settings:

```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=your-database-url
```

### Settings
Key settings in `request_tracker/settings.py`:

- `INSTALLED_APPS`: Includes 'service_requests' app
- `DATABASES`: SQLite configuration
- `STATIC_URL`: Static files configuration

## Development

### Project Structure
```
request-tracking-system/
├── request_tracker/          # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── service_requests/         # Main application
│   ├── models.py            # Database models
│   ├── views.py             # View logic
│   ├── forms.py             # Form definitions
│   ├── urls.py              # URL routing
│   ├── admin.py             # Admin configuration
│   └── templates/           # HTML templates
├── manage.py                # Django management
├── db.sqlite3              # Database file
└── README.md               # This file
```

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## API Documentation

### AJAX Endpoints

#### Update Request Status
- **URL**: `/requests/<id>/update-status/`
- **Method**: POST
- **Headers**: `Content-Type: application/json`, `X-CSRFToken: <token>`
- **Body**: `{"status": "new_status"}`
- **Response**: `{"success": true, "message": "Status updated", "new_status": "resolved"}`

### External API Integration

#### JSONPlaceholder API
- **Endpoint**: `https://jsonplaceholder.typicode.com/users`
- **Purpose**: Fetch department data from user companies
- **Fallback**: Static department list if API fails
- **Rate Limiting**: 5-second timeout with error handling

## Security Considerations

- CSRF protection enabled for all forms
- Authentication required for admin functions
- SQL injection protection via Django ORM
- XSS protection via template auto-escaping
- Admin interface restricted to staff users

## Deployment

### Production Checklist
- [ ] Set `DEBUG = False`
- [ ] Configure proper `SECRET_KEY`
- [ ] Set up proper database (PostgreSQL recommended)
- [ ] Configure static files serving
- [ ] Set up HTTPS
- [ ] Configure email backend for notifications
- [ ] Set up proper logging

### Docker Deployment (Optional)
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Check internet connectivity
   - Verify JSONPlaceholder API availability
   - System falls back to static departments automatically

2. **Database Errors**
   - Run `python manage.py migrate`
   - Check database permissions

3. **Static Files Not Loading**
   - Run `python manage.py collectstatic`
   - Check `STATIC_URL` settings

### Support

For technical support or feature requests, please create an issue in the repository.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### v1.0.0 (Initial Release)
- Basic request submission and management
- Admin dashboard with statistics
- External API integration
- Authentication system
- Responsive design
- Automation features

---

**Built with Django** | **Powered by Bootstrap** | **Icons by Font Awesome**