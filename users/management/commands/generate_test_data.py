from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import User
from courses.models import Course, Session
from attendance.models import AttendanceRecord
from notifications.models import Notification
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Generate test data for development'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating test users...')
        
        # Create admin
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            user_type=3
        )

        # Create staff/instructors
        instructors = []
        for i in range(3):
            instructor = User.objects.create_user(
                username=f'instructor{i+1}',
                email=f'instructor{i+1}@example.com',
                password='instructor123',
                user_type=2,
                first_name=f'Instructor{i+1}',
                last_name='Smith'
            )
            instructors.append(instructor)

        # Create students
        students = []
        for i in range(10):
            student = User.objects.create_user(
                username=f'student{i+1}',
                email=f'student{i+1}@example.com',
                password='student123',
                user_type=1,
                first_name=f'Student{i+1}',
                last_name='Doe'
            )
            students.append(student)

        self.stdout.write('Creating courses...')
        courses = []
        subjects = ['Python', 'Java', 'Web Development', 'Mobile Apps', 'Data Structures']
        days_patterns = ['0,2,4', '1,3', '2,4']  # Mon,Wed,Fri | Tue,Thu | Wed,Fri
        times = ['09:00', '11:00', '14:00', '16:00']

        for i, subject in enumerate(subjects):
            course = Course.objects.create(
                code=f'CS{101+i}',
                title=f'Introduction to {subject}',
                description=f'Learn the basics of {subject} programming',
                instructor=instructors[i % len(instructors)],
                start_date=timezone.now().date(),
                end_date=(timezone.now() + timedelta(days=90)).date(),
                schedule_days=days_patterns[i % len(days_patterns)],
                schedule_time=timezone.datetime.strptime(times[i % len(times)], '%H:%M').time(),
                session_duration=90,
                auto_schedule_enabled=True,
                location_latitude=random.uniform(40.0, 41.0),
                location_longitude=random.uniform(-74.0, -73.0),
                location_radius=100
            )
            # Add students to course
            for student in students[i::2]:  # Distribute students across courses
                course.students.add(student)
            courses.append(course)

        self.stdout.write('Generating sessions...')
        # Generate sessions for each course
        for course in courses:
            sessions = course.generate_sessions(
                start_date=timezone.now().date(),
                end_date=timezone.now().date() + timedelta(days=30)
            )
            Session.objects.bulk_create(sessions)

            # Create some past sessions with attendance
            past_sessions = []
            for i in range(5):
                past_session = Session.objects.create(
                    course=course,
                    title=f'Past Session {i+1}',
                    start_time=timezone.now() - timedelta(days=i+1, hours=2),
                    end_time=timezone.now() - timedelta(days=i+1),
                    location_latitude=course.location_latitude,
                    location_longitude=course.location_longitude,
                    radius=course.location_radius,
                    is_active=False
                )
                past_sessions.append(past_session)

            # Create attendance records for past sessions
            for session in past_sessions:
                for student in course.students.all():
                    # Randomly mark some students absent
                    if random.random() > 0.2:  # 80% attendance rate
                        AttendanceRecord.objects.create(
                            student=student,
                            session=session,
                            status='present',
                            latitude=session.location_latitude + random.uniform(-0.001, 0.001),
                            longitude=session.location_longitude + random.uniform(-0.001, 0.001),
                            biometric_data='test_biometric_data',
                            verified=True
                        )
                        # Create notification for successful attendance
                        Notification.objects.create(
                            recipient=student,
                            title='Attendance Recorded',
                            message=f'Your attendance for {session.title} has been recorded.',
                            notification_type='attendance',
                            related_object_id=session.id,
                            related_content_type='session'
                        )

        self.stdout.write(self.style.SUCCESS('Successfully generated test data'))
        
        self.stdout.write('\nTest Users Created:')
        self.stdout.write('Admin:')
        self.stdout.write('  Username: admin')
        self.stdout.write('  Password: admin123')
        self.stdout.write('\nInstructors:')
        for i in range(3):
            self.stdout.write(f'  Username: instructor{i+1}')
            self.stdout.write('  Password: instructor123')
        self.stdout.write('\nStudents:')
        for i in range(10):
            self.stdout.write(f'  Username: student{i+1}')
            self.stdout.write('  Password: student123') 