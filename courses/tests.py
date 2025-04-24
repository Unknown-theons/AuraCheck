from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from users.models import User
from .models import Course, Session
import json

# Create your tests here.

class CourseModelTest(TestCase):
    def setUp(self):
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
            end_date=(timezone.now() + timedelta(days=90)).date(),
            schedule_days='0,2,4',  # Monday, Wednesday, Friday
            schedule_time=datetime.strptime('09:00', '%H:%M').time(),
            session_duration=60,
            auto_schedule_enabled=True,
            location_latitude=12.34,
            location_longitude=56.78,
            location_radius=100
        )
        self.course.students.add(self.student)

    def test_course_creation(self):
        self.assertEqual(self.course.code, 'CS101')
        self.assertEqual(self.course.instructor, self.instructor)
        self.assertTrue(self.course.students.filter(id=self.student.id).exists())

    def test_auto_schedule_generation(self):
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=14)
        sessions = self.course.generate_sessions(start_date, end_date)
        
        # Count expected sessions (only on Monday, Wednesday, Friday)
        expected_count = sum(1 for i in range(15) if (start_date + timedelta(days=i)).weekday() in [0, 2, 4])
        self.assertEqual(len(sessions), expected_count)

class SessionModelTest(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor',
            password='testpass123',
            user_type=2
        )
        self.course = Course.objects.create(
            code='CS101',
            title='Introduction to Programming',
            instructor=self.instructor,
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=90)).date()
        )
        self.session = Session.objects.create(
            course=self.course,
            title='Test Session',
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=1),
            location_latitude=12.34,
            location_longitude=56.78,
            radius=100
        )

    def test_session_creation(self):
        self.assertEqual(self.session.course, self.course)
        self.assertEqual(self.session.radius, 100)
        self.assertFalse(self.session.is_active)

class CourseViewTest(TestCase):
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

    def test_course_list(self):
        self.client.login(username='instructor', password='testpass123')
        response = self.client.get(reverse('course-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_course_detail(self):
        self.client.login(username='instructor', password='testpass123')
        response = self.client.get(reverse('course-detail', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], 'CS101')

    def test_auto_schedule(self):
        self.client.login(username='instructor', password='testpass123')
        self.course.auto_schedule_enabled = True
        self.course.schedule_days = '0,2,4'
        self.course.schedule_time = datetime.strptime('09:00', '%H:%M').time()
        self.course.save()

        response = self.client.post(
            reverse('course-auto-schedule', args=[self.course.id]),
            data=json.dumps({
                'start_date': timezone.now().date().strftime('%Y-%m-%d'),
                'end_date': (timezone.now().date() + timedelta(days=7)).strftime('%Y-%m-%d')
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()['sessions']) > 0)
