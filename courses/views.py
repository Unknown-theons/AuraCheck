from django.shortcuts import render
from rest_framework import generics, permissions, filters
from .models import Course, Session
from .serializers import CourseSerializer, SessionSerializer
from users.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from datetime import datetime


class CourseListView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['instructor', 'start_date', 'end_date']
    search_fields = ['code', 'title', 'description']

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 1:  # Student
            return user.enrolled_courses.all()
        elif user.user_type in [2, 3]:  # Staff or Admin
            return Course.objects.filter(instructor=user)
        return Course.objects.none()


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]


class SessionListView(generics.ListCreateAPIView):
    serializer_class = SessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['course', 'is_active']
    search_fields = ['title', 'description']

    def get_queryset(self):
        user = self.request.user
        course_id = self.request.query_params.get('course')

        if course_id:
            return Session.objects.filter(course_id=course_id)

        if user.user_type == 1:  # Student
            return Session.objects.filter(course__students=user)
        elif user.user_type in [2, 3]:  # Staff or Admin
            return Session.objects.filter(course__instructor=user)
        return Session.objects.none()

    def perform_create(self, serializer):
        if self.request.user.user_type not in [2, 3]:  # Only staff/admin can create
            raise permissions.PermissionDenied()
        serializer.save()


class SessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]

    def perform_update(self, serializer):
        instance = serializer.instance
        if 'is_active' in serializer.validated_data:
            # Additional logic when activating/deactivating sessions
            pass
        serializer.save()


class StartSessionView(generics.UpdateAPIView):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_active:
            return Response({'error': 'Session is already active'},
                            status=status.HTTP_400_BAD_REQUEST)

        instance.is_active = True
        instance.save()
        return Response(self.get_serializer(instance).data)


class CloseSessionView(generics.UpdateAPIView):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.is_active:
            return Response({'error': 'Session is not active'},
                            status=status.HTTP_400_BAD_REQUEST)

        instance.is_active = False
        instance.save()
        return Response(self.get_serializer(instance).data)


class AutoScheduleSessionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

        if not request.user == course.instructor and not request.user.user_type == 3:
            return Response({'error': 'Only course instructor or admin can auto-schedule sessions'},
                          status=status.HTTP_403_FORBIDDEN)

        if not course.auto_schedule_enabled:
            return Response({'error': 'Auto-scheduling is not enabled for this course'},
                          status=status.HTTP_400_BAD_REQUEST)

        # Optional date range parameters
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')

        try:
            if start_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if end_date:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'},
                          status=status.HTTP_400_BAD_REQUEST)

        sessions = course.generate_sessions(start_date, end_date)
        Session.objects.bulk_create(sessions)

        return Response({
            'message': f'Successfully created {len(sessions)} sessions',
            'sessions': SessionSerializer(sessions, many=True).data
        })