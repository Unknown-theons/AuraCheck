from django.urls import path
from . import views

urlpatterns = [
    path('', views.CourseListView.as_view(), name='course-list'),
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('<int:pk>/auto-schedule/', views.AutoScheduleSessionsView.as_view(), name='course-auto-schedule'),
    path('sessions/', views.SessionListView.as_view(), name='session-list'),
    path('sessions/<int:pk>/', views.SessionDetailView.as_view(), name='session-detail'),
    path('sessions/<int:pk>/start/', views.StartSessionView.as_view(), name='session-start'),
    path('sessions/<int:pk>/close/', views.CloseSessionView.as_view(), name='session-close'),
] 