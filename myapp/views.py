from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Attendance, Duty

User = get_user_model()

# ---------------------------
# Registration Views
# ---------------------------
def register_staff(request):
    if request.method == "POST":
        fullname = request.POST.get("fullname")
        email = request.POST.get("email")
        id_no = request.POST.get("id_no")
        role = request.POST.get("role")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register_staff")

        if User.objects.filter(id_number=id_no).exists():
            messages.error(request, "ID number already exists.")
            return redirect("register_staff")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("register_staff")

        user = User.objects.create_user(
            id_number=id_no,
            email=email,
            password=password,
            role=role,
            fullname=fullname 
        )

        messages.success(request, "Staff account created successfully! Please log in.")
        return redirect("login")

    return render(request, "myapp/register_staff.html")


def register_admin(request):
    if request.method == "POST":
        fullname = request.POST.get("fullname")
        email = request.POST.get("email")
        id_no = request.POST.get("id_no")
        access_code = request.POST.get("access_code")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if access_code != "WILDCAT-ADMIN-2025":
            messages.error(request, "Invalid admin access code.")
            return redirect("register_admin")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register_admin")

        if User.objects.filter(id_number=id_no).exists():
            messages.error(request, "ID number already exists.")
            return redirect("register_admin")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("register_admin")

        user = User.objects.create_superuser(
            id_number=id_no,
            email=email,
            password=password,
            fullname=fullname  
        )

        messages.success(request, "Administrator account created successfully! Please log in.")
        return redirect("login")

    return render(request, "myapp/register_admin.html")


# ---------------------------
# Login & Logout
# ---------------------------
def login_view(request):
    if request.method == "POST":
        id_no = request.POST.get("id_no")
        password = request.POST.get("password")
        role = request.POST.get("role")

        user = authenticate(request, username=id_no, password=password)

        if user is not None:
            if user.role != role:
                messages.error(request, "Invalid role selected for this account.")
                return redirect("login")

            login(request, user)
            request.session["role"] = user.role

            if user.role == "admin":
                return redirect("admin_dashboard")
            elif user.role in ["security-officer", "supervisor"]:
                return redirect("staff_dashboard")
            else:
                return redirect("home_page")
        else:
            messages.error(request, "Invalid ID number or password.")
            return redirect("login")

    return render(request, "myapp/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


# ---------------------------
# Home / Dashboards
# ---------------------------
def home_page(request):
    return render(request, "myapp/home_page.html")


@login_required(login_url="login")
def staff_dashboard(request):
    return render(request, "myapp/staff_dashboard.html")


@login_required(login_url="login")
def admin_dashboard(request):
    return render(request, "myapp/admin_dashboard.html")


# ---------------------------
# Profile Pages (NEW)
# ---------------------------
@login_required(login_url="login")
def admin_profile(request):
    if request.user.role != "admin":
        messages.error(request, "Access denied.")
        return redirect("home_page")

    return render(request, "myapp/admin_profile.html")


@login_required(login_url="login")
def staff_profile(request):
    if request.user.role not in ["security-officer", "supervisor"]:
        messages.error(request, "Access denied.")
        return redirect("home_page")

    return render(request, "myapp/staff_profile.html")


# ---------------------------
# Employee Views
# ---------------------------
@login_required(login_url="login")
def my_duties_view(request):
    duties = Duty.objects.filter(staff=request.user)

    if request.method == "POST":
        duty_id = request.POST.get("duty_id")
        duty = get_object_or_404(Duty, id=duty_id, staff=request.user)
        duty.status = "completed"
        duty.save()
        messages.success(request, f"{duty.title} marked as completed.")
        return redirect("my_duties")

    return render(request, "myapp/my_duties.html", {"duties": duties})


@login_required(login_url="login")
def attendance_dashboard(request):
    user = request.user
    latest = Attendance.objects.filter(user=user).order_by('-check_in').first()
    history = Attendance.objects.filter(user=user).order_by('-check_in')

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "checkin":
            Attendance.objects.create(user=user)
        elif action == "checkout" and latest and latest.check_out is None:
            latest.check_out = timezone.now()
            latest.save()
        return redirect("attendance_dashboard")

    return render(request, "myapp/attendance_dashboard.html", {
        "latest": latest,
        "history": history
    })


# ---------------------------
# Admin Views
# ---------------------------
@login_required(login_url="login")
def manage_staff(request):
    if request.user.role != "admin":
        messages.error(request, "Access denied.")
        return redirect("home_page")

    staff_list = User.objects.filter(role__in=["security-officer", "supervisor"])
    duty_list = Duty.objects.all().order_by("time_start")

    if request.method == "POST":
        name = request.POST.get("nameInput")
        place = request.POST.get("placeInput")
        status = request.POST.get("statusInput")

        staff_member = User.objects.filter(fullname=name).first()
        if staff_member and place and status:
            Duty.objects.create(
                staff=staff_member,
                title=f"Duty at {place}",
                location=place,
                status=status,
                time_start=timezone.now(),
                time_end=timezone.now() + timezone.timedelta(hours=8)
            )
            messages.success(request, f"Duty assigned to {name}")
            return redirect("manage_staff")

    context = {
        "staff_list": staff_list,
        "duty_list": duty_list
    }
    return render(request, "myapp/manage_staff.html", context)


# ---------------------------
# Reports Page (NEW)
# ---------------------------
@login_required(login_url="login")
def reports(request):
    if request.user.role != "admin":
        messages.error(request, "Access denied.")
        return redirect("home_page")

    return render(request, "myapp/reports.html")
