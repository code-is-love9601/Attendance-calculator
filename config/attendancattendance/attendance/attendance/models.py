import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    student_id = models.CharField(max_length=40, unique=True)
    course = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.student_id} - {self.user.username}"


class AttendanceSession(models.Model):
    title = models.CharField(max_length=120)
    course = models.CharField(max_length=100, blank=True)
    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attendance_sessions",
    )
    created_at = models.DateTimeField(default=timezone.now)
    is_open = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class AttendanceRecord(models.Model):
    session = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE,
        related_name="records",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )
    marked_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["session", "student"],
                name="one_record_per_student_per_session",
            )
        ]
        ordering = ["-marked_at"]

    def __str__(self):
        return f"{self.student.username} - {self.session.title}"
