

from django.urls import path

from .views import (
    # Authentication
    login_view,
    logout_view,

    # Dashboards
    dashboard_view,
    employee_dashboard,

    # User Management
    users_list,
    user_add_view,
    user_edit_view,
    user_delete_view,

    # Attendance
    attendance_view,
    attendance_manage,
    update_hours,

    approve_attendance,
    reject_attendance,

    # Work Reports
    work_reports,
    work_report_add,
    work_report_approve,
    work_report_reject,

    # Material Requests
    material_requests,
    material_request_add,
    material_approve,
    material_reject,
)

app_name = "accounts"

urlpatterns = [
    # -------------------------
    # AUTHENTICATION
    # -------------------------
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    # -------------------------
    # DASHBOARDS
    # -------------------------
    path("dashboard/", dashboard_view, name="dashboard"),  # Admin / Supervisor
    path("employee-dashboard/", employee_dashboard, name="employee_dashboard"),  # Employee

    # -------------------------
    # USER MANAGEMENT
    # -------------------------
    path("users/", users_list, name="users"),
    path("users/add/", user_add_view, name="add_user"),
    path("users/edit/<int:user_id>/", user_edit_view, name="edit_user"),
    path("users/delete/<int:user_id>/", user_delete_view, name="delete_user"),

    # -------------------------
    # ATTENDANCE
    # -------------------------
    path("attendance/", attendance_view, name="attendance"),
    path("attendance/manage/", attendance_manage, name="attendance_manage"),
    path("attendance/update-hours/<int:pk>/", update_hours, name="update_hours"),

    path("attendance/approve/<int:pk>/", approve_attendance, name="approve_attendance"),
    path("attendance/reject/<int:pk>/", reject_attendance, name="reject_attendance"),

    # -------------------------
    # WORK REPORTS
    # -------------------------
    path("work-reports/", work_reports, name="work_reports"),
    path('work-reports/add/', work_report_add, name='work_report_add'),

    path("work-reports/approve/<int:pk>/", work_report_approve, name="work_report_approve"),
    path("work-reports/reject/<int:pk>/", work_report_reject, name="work_report_reject"),

    # -------------------------
    # MATERIAL REQUESTS
    # -------------------------
    path("material-requests/", material_requests, name="material_requests"),
    path("material-requests/add/",material_request_add, name="material_request_add"),
    path("material-requests/approve/<int:pk>/", material_approve, name="material_approve"),
    path("material-requests/reject/<int:pk>/", material_reject, name="material_reject"),
]
