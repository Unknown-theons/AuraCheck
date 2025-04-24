from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Notification, FCMDevice
from .serializers import NotificationSerializer, FCMDeviceSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

# Create your views here.

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['read', 'notification_type']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

class MarkNotificationReadView(generics.UpdateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.read = True
        instance.save()
        return Response(self.get_serializer(instance).data)

class MarkAllNotificationsReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        Notification.objects.filter(recipient=request.user, read=False).update(read=True)
        return Response({'message': 'All notifications marked as read'})

class RegisterFCMDeviceView(generics.CreateAPIView):
    serializer_class = FCMDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Deactivate old tokens for this user
        FCMDevice.objects.filter(
            user=self.request.user,
            registration_id=serializer.validated_data['registration_id']
        ).update(active=False)
        
        # Create new device
        serializer.save(user=self.request.user)

class UnregisterFCMDeviceView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        registration_id = request.data.get('registration_id')
        if not registration_id:
            return Response(
                {'error': 'registration_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        FCMDevice.objects.filter(
            user=request.user,
            registration_id=registration_id
        ).update(active=False)
        
        return Response({'message': 'Device unregistered successfully'})
