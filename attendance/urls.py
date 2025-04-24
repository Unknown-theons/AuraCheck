from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.SubmitAttendanceView.as_view(), name='submit-attendance'),
    path('student/', views.StudentAttendanceListView.as_view(), name='student-attendance-list'),
    path('report/', views.AttendanceReportView.as_view(), name='attendance-report'),
] 