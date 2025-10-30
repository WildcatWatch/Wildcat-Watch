from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Attendance

User = get_user_model()

<<<<<<< HEAD

=======
>>>>>>> cbdd753 (Fixed security role for login and views.py)
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

<<<<<<< HEAD


=======
>>>>>>> cbdd753 (Fixed security role for login and views.py)
def login_view(request):
    if request.method == "POST":
        id_no = request.POST.get("id_no")
        password = request.POST.get("password")
        role = request.POST.get("role")

        # Use 'username' because Django expects USERNAME_FIELD name
        user = authenticate(request, username=id_no, password=password)

        if user is not None:
            print("User authenticated successfully:", user)
            print("Role from DB:", user.role)
            print("Selected role from form:", role)

            if user.role != role:
                messages.error(request, "Invalid role selected for this account.")
                return redirect("login")

            login(request, user)
            request.session["role"] = user.role  # optional: store role in session

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


@login_required
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


@login_required
def attendance_dashboard(request):
    """Display the attendance page and handle check-in/out actions."""
    user = request.user

    # Get user's latest attendance record
    latest = Attendance.objects.filter(user=user).order_by('-check_in').first()

    # Get attendance history
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


def logout_view(request):
    logout(request)
    return redirect("login")


def home_page(request):
    return render(request, "myapp/home_page.html")

@login_required(login_url="login")
def staff_dashboard(request):
    return render(request, "myapp/staff_dashboard.html")

@login_required(login_url="login")
def admin_dashboard(request):
    return render(request, "myapp/admin_dashboard.html")

@login_required(login_url="login")
def my_duties(request):
    return render(request, "myapp/my_duties.html")

@login_required(login_url="login")
def attendance(request):
    return render(request, "myapp/attendance_dashboard.html")
