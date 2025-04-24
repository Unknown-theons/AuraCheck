from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # Override inherited ManyToMany fields to avoid reverse accessor clashes
    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='users_group_users',
        related_query_name='user_users',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='users_permission_users',
        related_query_name='perm_users',
    )
    USER_TYPE_CHOICES = (
        (1, 'Student'),
        (2, 'Staff'),
        (3, 'Admin'),
    )
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    # Additional student-specific fields
    student_id = models.CharField(max_length=20, blank=True, null=True)
    enrollment_date = models.DateField(blank=True, null=True)

    # Additional staff-specific fields
    staff_id = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True)