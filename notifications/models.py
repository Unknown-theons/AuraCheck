from django.db import models
from users.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from firebase_admin import messaging
import firebase_admin
from firebase_admin import credentials
import os
from django.conf import settings

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate(
        os.path.join(settings.BASE_DIR, 'firebase-service-account.json')
    )
    firebase_admin.initialize_app(cred)

class FCMDevice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    registration_id = models.TextField()
    active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'registration_id')

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('attendance', 'Attendance'),
        ('session', 'Session'),
        ('course', 'Course'),
        ('system', 'System'),
    )
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    related_content_type = models.CharField(max_length=50, null=True, blank=True)
    sent_to_device = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def send_to_device(self):
        """Send notification to user's FCM devices"""
        if self.sent_to_device:
            return
        
        devices = FCMDevice.objects.filter(user=self.recipient, active=True)
        
        for device in devices:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=self.title,
                    body=self.message,
                ),
                data={
                    'type': self.notification_type,
                    'object_id': str(self.related_object_id or ''),
                    'content_type': self.related_content_type or '',
                },
                token=device.registration_id,
            )
            
            try:
                messaging.send(message)
                self.sent_to_device = True
                self.save()
            except Exception as e:
                if 'registration-token-not-registered' in str(e):
                    device.active = False
                    device.save()

@receiver(post_save, sender=Notification)
def send_notification(sender, instance, created, **kwargs):
    """Send notification when created"""
    if created:
        instance.send_to_device()