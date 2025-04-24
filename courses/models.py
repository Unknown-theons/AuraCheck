from django.db import models
from django.db import models
from users.models import User


class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type__in': [2, 3]})
    students = models.ManyToManyField(User, related_name='enrolled_courses', limit_choices_to={'user_type': 1})
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Auto-schedule fields
    schedule_days = models.CharField(max_length=20, blank=True, help_text="Comma-separated days (0-6, 0=Monday)")
    schedule_time = models.TimeField(null=True, blank=True, help_text="Daily start time for sessions")
    session_duration = models.PositiveIntegerField(default=60, help_text="Session duration in minutes")
    auto_schedule_enabled = models.BooleanField(default=False)
    location_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_radius = models.PositiveIntegerField(default=100, help_text="Radius in meters")

    def __str__(self):
        return f"{self.code} - {self.title}"

    def generate_sessions(self, start_date=None, end_date=None):
        """Generate sessions based on schedule settings"""
        from datetime import datetime, timedelta
        import pytz

        if not self.auto_schedule_enabled or not self.schedule_days or not self.schedule_time:
            return []

        start = start_date or self.start_date
        end = end_date or self.end_date
        days = [int(d.strip()) for d in self.schedule_days.split(',')]
        
        current = start
        sessions = []
        
        while current <= end:
            if current.weekday() in days:
                session_start = datetime.combine(
                    current,
                    self.schedule_time
                ).replace(tzinfo=pytz.UTC)
                
                session_end = session_start + timedelta(minutes=self.session_duration)
                
                session = Session(
                    course=self,
                    title=f"{self.code} - {current.strftime('%Y-%m-%d')}",
                    description=f"Auto-generated session for {self.title}",
                    start_time=session_start,
                    end_time=session_end,
                    location_latitude=self.location_latitude,
                    location_longitude=self.location_longitude,
                    radius=self.location_radius
                )
                sessions.append(session)
            
            current += timedelta(days=1)
        
        return sessions


class Session(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    location_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    radius = models.PositiveIntegerField(default=100)  # in meters
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['start_time']