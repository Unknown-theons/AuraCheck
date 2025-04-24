# Attendance System Backend

A Django-based backend for a Flutter attendance tracking application. This system provides APIs for managing courses, sessions, and attendance records with features like GPS verification and biometric authentication.

## Features

- User Authentication (Students, Staff, Admin)
- Course Management
- Session Scheduling (Manual and Automatic)
- Attendance Tracking with GPS Verification
- Biometric Authentication Support
- Notifications System
- Report Generation (PDF/Excel)
- API Documentation with Swagger

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

## API Documentation

The API documentation is available at:
- Swagger UI: `/swagger/`
- ReDoc: `/redoc/`
- OpenAPI JSON: `/swagger.json`

## Key Endpoints

### Authentication
- `POST /api/users/login/` - User login
- `POST /api/users/logout/` - User logout
- `GET /api/users/profile/` - Get user profile
- `PUT /api/users/profile/` - Update user profile

### Courses
- `GET /api/courses/` - List courses
- `POST /api/courses/` - Create course
- `GET /api/courses/<id>/` - Get course details
- `PUT /api/courses/<id>/` - Update course
- `DELETE /api/courses/<id>/` - Delete course
- `POST /api/courses/<id>/auto-schedule/` - Generate sessions automatically

### Sessions
- `GET /api/courses/sessions/` - List sessions
- `POST /api/courses/sessions/` - Create session
- `GET /api/courses/sessions/<id>/` - Get session details
- `PUT /api/courses/sessions/<id>/` - Update session
- `DELETE /api/courses/sessions/<id>/` - Delete session
- `POST /api/courses/sessions/<id>/start/` - Start session
- `POST /api/courses/sessions/<id>/close/` - Close session

### Attendance
- `POST /api/attendance/submit/` - Submit attendance
- `GET /api/attendance/history/` - Get attendance history
- `GET /api/attendance/report/` - Generate attendance report

### Notifications
- `GET /api/notifications/` - List notifications
- `PUT /api/notifications/<id>/read/` - Mark notification as read

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
Follow PEP 8 guidelines for Python code style.

## Flutter Integration

The backend is configured with CORS support for Flutter integration. The following settings are important for Flutter developers:

1. Base URL: `http://localhost:8000/api/`
2. Authentication: Bearer token in Authorization header
3. Content-Type: application/json

## Security Notes

1. Change `CORS_ALLOW_ALL_ORIGINS` to `False` in production
2. Configure proper CORS origins
3. Use environment variables for sensitive data
4. Enable HTTPS in production

## License

This project is licensed under the BSD License. 

mkdir -p users/management/commands 