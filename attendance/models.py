from django.db import models
from django.db import models
from users.models import User
from courses.models import Course, Session


class AttendanceRecord(models.Model):
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    )

    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 1})
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    biometric_data = models.TextField(null=True, blank=True)  # Store biometric verification data
    verified = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'session')