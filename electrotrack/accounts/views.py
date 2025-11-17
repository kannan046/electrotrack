from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone



from .models import Attendance, WorkReport, MaterialRequest
from .forms import WorkReportForm, MaterialRequestForm, LoginForm

User = get_user_model()


# ============================================
# LOGIN / LOGOUT
# ============================================
def login_view(request):
    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            # ✅ Ensure proper role-based redirect
            user_role = getattr(user, 'role', None)

            if user.is_superuser or user_role in ['admin', 'supervisor']:
                return redirect('accounts:dashboard')
            else:
                return redirect('accounts:employee_dashboard')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("accounts:login")


# ============================================
# DASHBOARDS
# ============================================
@login_required
def dashboard_view(request):
    """Admin / Supervisor dashboard"""
    if request.user.role not in ["admin", "supervisor"]:
        return redirect("accounts:employee_dashboard")
    return render(request, "accounts/dashboard.html")


@login_required
def employee_dashboard(request):
    """Employee dashboard"""
    if request.user.role in ["admin", "supervisor"]:
        return redirect("accounts:dashboard")
    return render(request, "accounts/employee_dashboard.html")


# ============================================
# USERS MANAGEMENT
# ============================================
@login_required
def users_list(request):
    users = User.objects.all()
    return render(request, "accounts/users.html", {"users": users})


@login_required
def user_add_view(request):
    if request.method == "POST":
        username = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")
        site_location = request.POST.get("site_location") 

        user = User.objects.create(username=username, email=email)
        if password:
            user.set_password(password)
        if hasattr(user, "role"):
            user.role = role
        user.save()
        
        if hasattr(user, "site_location"):
            user.site_location = site_location  # ✅ save it
        user.save()

        messages.success(request, "✅ User created successfully.")
        return redirect("accounts:users")

    return render(request, "accounts/user_add.html")


@login_required
def user_edit_view(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")

        user.username = name
        user.email = email
        if password:
            user.set_password(password)
        if hasattr(user, "role"):
            user.role = role
        user.save()

        messages.success(request, "✅ User updated successfully.")
        return redirect("accounts:users")

    return render(request, "accounts/user_edit.html", {"user": user})


@login_required
def user_delete_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, "🗑️ User deleted successfully.")
    return redirect("accounts:users")


# ============================================
# ATTENDANCE
# ============================================
@login_required
def attendance_view(request):
    """Employee attendance page"""
    user = request.user

    # ❌ Prevent admin/supervisor from marking attendance
    if user.role in ["admin", "supervisor"]:
        messages.info(request, "Admins and supervisors cannot mark attendance.")
        return redirect("accounts:attendance_manage")

    if request.method == "POST":
        action = request.POST.get("action")
        

        # --------- Get location safely ----------
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")

        try:
            latitude = float(latitude) if latitude else None
            longitude = float(longitude) if longitude else None
        except:
            latitude = None
            longitude = None

        # --------- Clock IN ----------
        if action == "clock_in":
            Attendance.objects.create(
                user=user,
                clock_in=timezone.now(),
                latitude=latitude,
                longitude=longitude,
                status="pending",
            )
            messages.success(request, "✅ Clock-in recorded successfully!")
            return redirect("accounts:attendance")

        # --------- Clock OUT ----------
        elif action == "clock_out":
            try:
                record = Attendance.objects.filter(
                    user=user, clock_out__isnull=True
                ).latest("id")

                record.clock_out = timezone.now()
                record.latitude = latitude
                record.longitude = longitude

                # --------- Calculate Total Hours ----------
                if record.clock_in:
                    duration = record.clock_out - record.clock_in
                    record.total_hours = round(duration.total_seconds() / 3600, 2)

                record.save()
                messages.success(request, "✅ Clock-out recorded successfully!")

            except Attendance.DoesNotExist:
                messages.warning(request, "⚠️ No active clock-in found!")

            return redirect("accounts:attendance")

    # --------- Show employee’s attendance ----------
    attendance_records = Attendance.objects.filter(user=user).order_by("-id")

    return render(
        request,
        "accounts/attendance.html",
        {"attendance": attendance_records}  # ✅ Correct variable name
    )

@login_required
def update_hours(request, pk):
    if request.method == "POST":
        hours = request.POST.get("hours")
        try:
            hours = float(hours)
        except:
            hours = 0

        record = Attendance.objects.get(id=pk)
        record.total_hours = hours
        record.save()

        messages.success(request, "Hours updated successfully!")
        return redirect("accounts:attendance_manage")



@login_required
def attendance_manage(request):
    """Admin/Supervisor view"""
    if request.user.role == "admin":
        attendance_list = Attendance.objects.all().order_by("-id")
    elif request.user.role == "supervisor":
        attendance_list = Attendance.objects.filter(supervisor=request.user).order_by("-id")
    else:
        # employees should not access this
        return redirect("accounts:attendance")

    return render(request, "accounts/attendance_manage.html", {"attendance_list": attendance_list})


@login_required
def approve_attendance(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    attendance.status = "approved"
    attendance.save()
    messages.success(request, "✅ Attendance approved.")
    return redirect("accounts:attendance_manage")


@login_required
def reject_attendance(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    attendance.status = "rejected"
    attendance.save()
    messages.warning(request, "❌ Attendance rejected.")
    return redirect("accounts:attendance_manage")


# ============================================
# WORK REPORTS
# ============================================
@login_required
def work_reports(request):
    """Admin and supervisors can see all reports; employees see their own."""
    if request.user.role == "admin":
        reports = WorkReport.objects.all().order_by("-created_at")
    elif request.user.role == "supervisor":
        reports = WorkReport.objects.filter(user__supervisor=request.user).order_by("-created_at")
    else:
        reports = WorkReport.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "accounts/work_reports.html", {"reports": reports})



# views.py
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# ... your other imports above ...

@login_required
def work_report_add(request):
    """
    Accepts normal form POST (redirect) and AJAX (JSON) POST submissions.
    URL name: accounts:work_report_add
    """
    if request.method == "POST":
        form = WorkReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            # optionally assign supervisor/branch if you store that:
            if hasattr(request.user, "supervisor"):
                report.supervisor = request.user.supervisor
            report.save()

            # If AJAX request, return JSON success
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "message": "Work report submitted successfully."})
            # else normal POST flow
            messages.success(request, "Work report submitted successfully.")
            return redirect('accounts:work_reports')
        else:
            # invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                # send back first error message as JSON
                errors = form.errors.as_json()
                return JsonResponse({"success": False, "message": "Validation failed.", "errors": errors}, status=400)

    else:
        form = WorkReportForm()

    # GET — render normal page for /work-reports/add/ (non-AJAX flow)
    return render(request, "accounts/work_report_add.html", {"form": form})


@login_required
def work_report_approve(request, pk):
    report = get_object_or_404(WorkReport, pk=pk)
    report.status = "approved"
    report.save()
    messages.success(request, "✅ Work report approved.")
    return redirect("accounts:work_reports")


@login_required
def work_report_reject(request, pk):
    report = get_object_or_404(WorkReport, pk=pk)
    report.status = "rejected"
    report.save()
    messages.warning(request, "❌ Work report rejected.")
    return redirect("accounts:work_reports")


# ============================================
# MATERIAL REQUESTS
# ============================================


@login_required
def material_request_add(request):
    """Employee Raise Material Request"""
    user = request.user

    # ✅ Prevent Admin/Supervisor from raising requests
    if user.role in ["admin", "supervisor"]:
        return redirect("accounts:material_requests")

    if request.method == "POST":
        # ✅ Extract multiple rows from form (no [] in key names)
        item_names = request.POST.getlist("item_name")
        quantities = request.POST.getlist("quantity")
        units = request.POST.get("unit")
        description = request.POST.get("description")
        photo = request.FILES.get("photo")  # ✅ handle uploaded photo

        # ✅ Validation
        if not item_names or not quantities:
            messages.error(request, "⚠️ Please enter at least one material item.")
            return redirect("accounts:material_request_add")

        # ✅ Save each material item as a separate entry
        for i in range(len(item_names)):
            item_name = item_names[i].strip()
            quantity = quantities[i]
            unit = units[i] if i < len(units) else ""

            if item_name and quantity:
                MaterialRequest.objects.create(
                    user=user,
                    item_name=f"{item_name}" ,
                    quantity=quantity,
                    unit=unit,
                    description=description,
                    photo=photo,  # ✅ attach photo
                    status="pending"
                )

        messages.success(request, "✅ Material request submitted successfully!")
        return redirect("accounts:employee_dashboard")

    # ✅ Render form with auto-filled info
    return render(request, "accounts/material_request_add.html", {
        "now": timezone.now(),
        "department": user.get_full_name() or user.username,
    })


    

@login_required
def material_requests(request):
    """Admin & Supervisor View All Material Requests"""
    if request.user.role in ["admin", "supervisor"]:
        requests = MaterialRequest.objects.select_related('user').order_by('-created_at')
    else:
        requests = MaterialRequest.objects.filter(user=request.user).order_by('-created_at')

    return render(request, "accounts/material_requests.html", {"requests": requests})


@login_required
def material_approve(request, pk):
    req = get_object_or_404(MaterialRequest, pk=pk)
    req.status = "approved"
    req.save()
    messages.success(request, "✅ Material request approved.")
    return redirect("accounts:material_requests")


@login_required
def material_reject(request, pk):
    req = get_object_or_404(MaterialRequest, pk=pk)
    req.status = "rejected"
    req.save()
    messages.warning(request, "❌ Material request rejected.")
    return redirect("accounts:material_requests")
