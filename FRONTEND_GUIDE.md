# Frontend Integration Guide

## Setup and Testing

1. The backend server runs at: `http://localhost:8000`
2. Test accounts are available after running:
   ```bash
   python manage.py generate_test_data
   ```

### Test Accounts
- Admin: `admin/admin123`
- Instructors: `instructor1/instructor123` to `instructor3/instructor123`
- Students: `student1/student123` to `student10/student123`

## API Integration

### 1. Authentication

```dart
// Login
final response = await http.post(
  Uri.parse('http://localhost:8000/api/users/login/'),
  body: {
    'username': username,
    'password': password,
  },
);

// Store the token
final token = jsonDecode(response.body)['token'];

// Use token in subsequent requests
final headers = {
  'Authorization': 'Bearer $token',
  'Content-Type': 'application/json',
};
```

### 2. Course Management

```dart
// Get user's courses
final response = await http.get(
  Uri.parse('http://localhost:8000/api/courses/'),
  headers: headers,
);

// Course response format:
{
  "id": 1,
  "code": "CS101",
  "title": "Introduction to Python",
  "description": "Learn Python basics",
  "instructor": {
    "id": 2,
    "username": "instructor1",
    "first_name": "Instructor1",
    "last_name": "Smith"
  },
  "start_date": "2024-03-10",
  "end_date": "2024-06-10",
  "schedule_days": "0,2,4",
  "schedule_time": "09:00:00",
  "location_latitude": 40.7128,
  "location_longitude": -74.0060,
  "location_radius": 100
}
```

### 3. Session Management

```dart
// Get course sessions
final response = await http.get(
  Uri.parse('http://localhost:8000/api/courses/sessions/?course=1'),
  headers: headers,
);

// Session response format:
{
  "id": 1,
  "title": "CS101 - 2024-03-10",
  "start_time": "2024-03-10T09:00:00Z",
  "end_time": "2024-03-10T10:30:00Z",
  "is_active": true,
  "location_latitude": 40.7128,
  "location_longitude": -74.0060,
  "radius": 100
}
```

### 4. Attendance Submission

```dart
// Get current location
Position position = await Geolocator.getCurrentPosition();

// Submit attendance
final response = await http.post(
  Uri.parse('http://localhost:8000/api/attendance/submit/'),
  headers: headers,
  body: jsonEncode({
    'session': sessionId,
    'latitude': position.latitude,
    'longitude': position.longitude,
    'biometric_data': biometricData, // Optional
  }),
);
```

### 5. Notifications

```dart
// Get user's notifications
final response = await http.get(
  Uri.parse('http://localhost:8000/api/notifications/'),
  headers: headers,
);

// Register FCM token
final response = await http.post(
  Uri.parse('http://localhost:8000/api/notifications/devices/register/'),
  headers: headers,
  body: jsonEncode({
    'registration_id': fcmToken,
  }),
);
```

## Required Flutter Packages

```yaml
dependencies:
  http: ^1.1.0
  geolocator: ^10.0.0
  firebase_core: ^2.24.0
  firebase_messaging: ^14.7.6
  flutter_local_notifications: ^16.2.0
```

## Features to Implement

1. Authentication Screens:
   - Login
   - Profile view/edit

2. Course Screens:
   - Course list
   - Course details
   - Session schedule

3. Attendance Features:
   - Location permission handling
   - GPS verification
   - Attendance submission
   - Attendance history

4. Notification System:
   - FCM setup
   - Notification list
   - Real-time updates

## Location Handling

1. Request permissions:
```dart
await Geolocator.requestPermission();
```

2. Check if user is within session radius:
```dart
double distanceInMeters = Geolocator.distanceBetween(
  userLat, userLng,
  sessionLat, sessionLng
);
bool isWithinRadius = distanceInMeters <= session.radius;
```

## Error Handling

Common API response codes:
- 200: Success
- 201: Created
- 400: Bad request
- 401: Unauthorized
- 403: Forbidden
- 404: Not found

Example error handling:
```dart
try {
  final response = await http.post(...);
  if (response.statusCode == 201) {
    // Success
  } else {
    final error = jsonDecode(response.body);
    // Show error message
  }
} catch (e) {
  // Handle network errors
}
```

## Testing Flow

1. Login as different user types to test different views
2. Test attendance submission:
   - Within radius
   - Outside radius
   - Duplicate submission
3. Test session flow:
   - View active sessions
   - Submit attendance
   - View history
4. Test notifications:
   - FCM token registration
   - Receiving notifications
   - Notification list view

## Need Help?

The complete API documentation is available at:
- Swagger UI: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/` 