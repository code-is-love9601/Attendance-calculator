from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("students/", views.students, name="students"),
    path("sessions/create/", views.create_session, name="create_session"),
    path("sessions/<int:session_id>/", views.session_detail, name="session_detail"),
    path("scan/<uuid:token>/", views.scan_attendance, name="scan_attendance"),
]
