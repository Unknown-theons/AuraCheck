from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from users.models import User
from courses.models import Course, Session
from .models import AttendanceRecord
import json

class AttendanceTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.instructor = User.objects.create_user(
            username='instructor',
            password='testpass123',
            user_type=2
        )
        self.student = User.objects.create_user(
            username='student',
            password='testpass123',
            user_type=1
        )
        self.course = Course.objects.create(
            code='CS101',
            title='Introduction to Programming',
            instructor=self.instructor,
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=90)).date()
        )
        self.course.students.add(self.student)
        
        self.session = Session.objects.create(
            course=self.course,
            title='Test Session',
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=1),
            location_latitude=12.34,
            location_longitude=56.78,
            radius=100,
            is_active=True
        )

    def test_submit_attendance(self):
        self.client.login(username='student', password='testpass123')
        response = self.client.post(
            reverse('submit-attendance'),
            data=json.dumps({
                'session': self.session.id,
                'latitude': 12.34,
                'longitude': 56.78,
                'biometric_data': 'test_biometric_data'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(AttendanceRecord.objects.filter(
            student=self.student,
            session=self.session
        ).exists())

    def test_duplicate_attendance(self):
        self.client.login(username='student', password='testpass123')
        # First submission
        self.client.post(
            reverse('submit-attendance'),
            data=json.dumps({
                'session': self.session.id,
                'latitude': 12.34,
                'longitude': 56.78,
                'biometric_data': 'test_biometric_data'
            }),
            content_type='application/json'
        )
        
        # Duplicate submission
        response = self.client.post(
            reverse('submit-attendance'),
            data=json.dumps({
                'session': self.session.id,
                'latitude': 12.34,
                'longitude': 56.78,
                'biometric_data': 'test_biometric_data'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            AttendanceRecord.objects.filter(student=self.student, session=self.session).count(),
            1
        )

    def test_out_of_range_attendance(self):
        self.client.login(username='student', password='testpass123')
        response = self.client.post(
            reverse('submit-attendance'),
            data=json.dumps({
                'session': self.session.id,
                'latitude': 13.34,  # Different location
                'longitude': 57.78,
                'biometric_data': 'test_biometric_data'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(AttendanceRecord.objects.filter(
            student=self.student,
            session=self.session
        ).exists())

    def test_attendance_history(self):
        self.client.login(username='student', password='testpass123')
        # Create some attendance records
        AttendanceRecord.objects.create(
            student=self.student,
            session=self.session,
            status='present',
            latitude=12.34,
            longitude=56.78,
            biometric_data='test_data',
            verified=True
        )
        
        response = self.client.get(reverse('attendance-history'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_attendance_report(self):
        self.client.login(username='instructor', password='testpass123')
        # Create some attendance records
        AttendanceRecord.objects.create(
            student=self.student,
            session=self.session,
            status='present',
            latitude=12.34,
            longitude=56.78,
            biometric_data='test_data',
            verified=True
        )
        
        # Test JSON format
        response = self.client.get(
            reverse('attendance-report'),
            {'course': self.course.id, 'format': 'json'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        
        # Test PDF format
        response = self.client.get(
            reverse('attendance-report'),
            {'course': self.course.id, 'format': 'pdf'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
        # Test Excel format
        response = self.client.get(
            reverse('attendance-report'),
            {'course': self.course.id, 'format': 'excel'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.ms-excel')
