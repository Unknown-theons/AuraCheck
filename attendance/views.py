from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import AttendanceRecord
from .serializers import AttendanceRecordSerializer
from courses.models import Session, Course
from users.models import User
from django.utils import timezone
import math
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from io import BytesIO
import pandas as pd


class SubmitAttendanceView(generics.CreateAPIView):
    serializer_class = AttendanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if request.user.user_type != 1:
            return Response({'error': 'Only students can submit attendance'},
                            status=status.HTTP_403_FORBIDDEN)

        session_id = request.data.get('session')
        try:
            session = Session.objects.get(pk=session_id)
        except Session.DoesNotExist:
            return Response({'error': 'Session not found'},
                            status=status.HTTP_404_NOT_FOUND)

        # Check if session is active and within time window
        now = timezone.now()
        if not session.is_active:
            return Response({'error': 'Session is not active'},
                            status=status.HTTP_400_BAD_REQUEST)
        if now < session.start_time:
            return Response({'error': 'Session has not started yet'},
                            status=status.HTTP_400_BAD_REQUEST)
        if now > session.end_time:
            return Response({'error': 'Session has ended'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if attendance already exists
        if AttendanceRecord.objects.filter(student=request.user, session=session).exists():
            return Response({'error': 'Attendance already submitted for this session'},
                            status=status.HTTP_400_BAD_REQUEST)

        # GPS verification
        user_lat = float(request.data.get('latitude', 0))
        user_lng = float(request.data.get('longitude', 0))
        distance = self.calculate_distance(
            user_lat, user_lng,
            session.location_latitude, session.location_longitude
        )

        if distance > session.radius:
            return Response({'error': 'You are not within the allowed attendance radius'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Biometric verification
        biometric_data = request.data.get('biometric_data')
        if not self.verify_biometric_data(biometric_data, request.user):
            return Response({'error': 'Biometric verification failed'},
                            status=status.HTTP_400_BAD_REQUEST)

        attendance_data = {
            'student': request.user.id,
            'session': session.id,
            'status': 'present',
            'latitude': user_lat,
            'longitude': user_lng,
            'biometric_data': biometric_data,
            'verified': True
        }

        serializer = self.get_serializer(data=attendance_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def verify_biometric_data(self, biometric_data, user):
        """
        Verify the biometric data against the user's stored template.
        This is a placeholder implementation that should be replaced with actual biometric verification.
        """
        if not biometric_data:
            return False
            
        try:
            # TODO: Implement actual biometric verification here
            # For now, we'll just check if the data is not empty
            # In a real implementation, this would:
            # 1. Load the user's stored biometric template
            # 2. Compare the submitted data against the template
            # 3. Return True only if the match score exceeds a threshold
            return bool(biometric_data.strip())
        except Exception as e:
            return False

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        # Haversine formula to calculate distance between two GPS points
        R = 6371000  # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (math.sin(delta_phi / 2) ** 2 + 
             math.cos(phi1) * math.cos(phi2) * 
             math.sin(delta_lambda / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c


class StudentAttendanceListView(generics.ListAPIView):
    serializer_class = AttendanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AttendanceRecord.objects.filter(student=self.request.user)


# attendance/views.py


class AttendanceReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        course_id = request.query_params.get('course')
        format = request.query_params.get('format', 'json')

        if not course_id:
            return Response({'error': 'Course ID is required'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'},
                            status=status.HTTP_404_NOT_FOUND)

        attendance_data = AttendanceRecord.objects.filter(
            session__course=course
        ).select_related('student', 'session')

        if format == 'pdf':
            return self.generate_pdf_report(attendance_data, course)
        elif format == 'excel':
            return self.generate_excel_report(attendance_data, course)
        else:
            serializer = AttendanceRecordSerializer(attendance_data, many=True)
            return Response(serializer.data)

    def generate_pdf_report(self, data, course):
        buffer = BytesIO()
        p = canvas.Canvas(buffer)

        # PDF generation logic
        p.drawString(100, 800, f"Attendance Report for {course.code} - {course.title}")
        y_position = 780
        for record in data:
            p.drawString(100, y_position,
                         f"{record.student.username}: {record.status} at {record.timestamp}")
            y_position -= 20
            if y_position < 50:
                p.showPage()
                y_position = 780

        p.save()
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{course.code}_attendance_report.pdf"'
        return response

    def generate_excel_report(self, data, course):
        df_data = []
        for record in data:
            df_data.append({
                'Student': record.student.username,
                'Status': record.status,
                'Date': record.timestamp.date(),
                'Time': record.timestamp.time(),
                'Location': f"{record.latitude}, {record.longitude}",
                'Verified': record.verified
            })

        df = pd.DataFrame(df_data)
        excel_file = BytesIO()
        df.to_excel(excel_file, index=False)
        excel_file.seek(0)

        response = HttpResponse(excel_file, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = f'attachment; filename="{course.code}_attendance_report.xlsx"'
        return response