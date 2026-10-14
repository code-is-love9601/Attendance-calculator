from django.contrib import admin
from .models import StudentProfile, AttendanceSession, AttendanceRecord

admin.site.register(StudentProfile)
admin.site.register(AttendanceSession)
admin.site.register(AttendanceRecord)
