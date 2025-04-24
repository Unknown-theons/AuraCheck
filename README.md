# AuraCheck  
**AI Secure Attendance Tracking System**  

## Project Goals  

### Provide Real-Time Attendance Information  
- Enable students to view their attendance records instantly through the app.  
- Display detailed data, such as attendance percentages for each subject.  

### Automate Attendance Input  
- Eliminate manual attendance entry and minimize errors.  

### User-Friendly Interface  
- Simple and interactive design.  

### Improve Efficiency, Accuracy, and Enable Anti-Cheat  
- Enable Prof/TA to open attendance whenever they like (e.g., mid-lecture, at the end of the lecture).  
- Provide the option to make attendance open for a fixed duration (e.g., 10 minutes, 20 minutes).  
- Require students to confirm attendance using **GPS and Fingerprint (biometric cryptographic key)**.  

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

## Team Structure

### Front-End Team Goals  

#### **User Interface**  
- Layout and design implementation
- Mobile-friendly responsive design

#### **User Interaction**  
- Intuitive navigation and controls

### Back-End Team Goals  

#### **Core Features**  
- Location Tracking Function
- Biometric Cryptographic Key based on Fingerprint
- Email Authentication
- Support front-end interactions

### Database Team Goals  

#### **Structure**  
- Tables, fields, and relationships
- Efficient data models

#### **Data Handling and Access**  
- Efficient storage and retrieval mechanisms

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
Follow PEP 8 guidelines for Python code style.

## License

This project is licensed under the BSD License.
