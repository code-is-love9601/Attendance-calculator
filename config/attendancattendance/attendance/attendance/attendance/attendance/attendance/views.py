import base64
import io

import qrcode

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .models import StudentProfile, AttendanceSession, AttendanceRecord


def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "home.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username", "").strip(),
            password=request.POST.get("password", ""),
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        messages.error(request, "Invalid username or password.")

    return render(request, "login.html")


@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")
    return redirect("dashboard")


@login_required
def dashboard(request):
    if request.user.is_staff:
        sessions = AttendanceSession.objects.filter(
            created_by=request.user
        ).order_by("-created_at")

        return render(request, "dashboard.html", {
            "is_staff": True,
            "sessions": sessions,
            "total_students": StudentProfile.objects.count(),
            "total_records": AttendanceRecord.objects.count(),
        })

    records = AttendanceRecord.objects.filter(
        student=request.user
    ).select_related("session")

    return render(request, "dashboard.html", {
        "is_staff": False,
        "records": records,
        "present_count": records.count(),
    })


@login_required
def students(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Teacher access required.")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        student_id = request.POST.get("student_id", "").strip()
        full_name = request.POST.get("full_name", "").strip()
        course = request.POST.get("course", "").strip()
        password = request.POST.get("password", "")

        if not all([username, student_id, password]):
            messages.error(request, "Required fields are missing.")

        elif (
            User.objects.filter(username=username).exists()
            or StudentProfile.objects.filter(student_id=student_id).exists()
        ):
            messages.error(request, "Username or student ID already exists.")

        elif len(password) < 8:
            messages.error(request, "Password must be at least 8 characters.")

        else:
            parts = full_name.split(" ", 1)
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=parts[0] if parts else "",
                last_name=parts[1] if len(parts) > 1 else "",
            )

            StudentProfile.objects.create(
                user=user,
                student_id=student_id,
                course=course,
            )

            messages.success(request, "Student account created.")
            return redirect("students")

    profiles = StudentProfile.objects.select_related("user").order_by("student_id")
    return render(request, "students.html", {"profiles": profiles})


@login_required
def create_session(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Teacher access required.")

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        course = request.POST.get("course", "").strip()

        if title:
            session = AttendanceSession.objects.create(
                title=title,
                course=course,
                created_by=request.user,
            )
            return redirect("session_detail", session_id=session.id)

        messages.error(request, "Session title is required.")

    return render(request, "create_session.html")


@login_required
def session_detail(request, session_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Teacher access required.")

    session = get_object_or_404(
        AttendanceSession,
        id=session_id,
        created_by=request.user,
    )

    scan_url = request.build_absolute_uri(f"/scan/{session.token}/")

    qr = qrcode.make(scan_url)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")

    qr_data = base64.b64encode(buffer.getvalue()).decode("ascii")
    records = session.records.select_related("student")

    return render(request, "session_detail.html", {
        "session": session,
        "scan_url": scan_url,
        "qr_data": qr_data,
        "records": records,
        "present_count": records.count(),
    })


@login_required
def scan_attendance(request, token):
    session = get_object_or_404(AttendanceSession, token=token)

    if request.method == "POST":
        if not session.is_open:
            messages.error(request, "This session is closed.")

        elif request.user.is_staff:
            messages.error(request, "Teacher accounts cannot mark attendance.")

        elif not StudentProfile.objects.filter(user=request.user).exists():
            messages.error(request, "Only registered students can mark attendance.")

        else:
            try:
                AttendanceRecord.objects.create(
                    session=session,
                    student=request.user,
                )
                messages.success(request, "Attendance marked successfully!")
            except IntegrityError:
                messages.info(request, "Attendance is already recorded.")

        return redirect("scan_attendance", token=token)

    already_marked = AttendanceRecord.objects.filter(
        session=session,
        student=request.user,
    ).exists()

    return render(request, "scan.html", {
        "session": session,
        "already_marked": already_marked,
    })
