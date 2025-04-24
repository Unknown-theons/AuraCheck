from django.urls import path
from .views import (
    NotificationListView,
    MarkNotificationReadView,
    MarkAllNotificationsReadView,
    RegisterFCMDeviceView,
    UnregisterFCMDeviceView
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/read/', MarkNotificationReadView.as_view(), name='mark-notification-read'),
    path('mark-all-read/', MarkAllNotificationsReadView.as_view(), name='mark-all-notifications-read'),
    path('devices/register/', RegisterFCMDeviceView.as_view(), name='register-fcm-device'),
    path('devices/unregister/', UnregisterFCMDeviceView.as_view(), name='unregister-fcm-device'),
] 