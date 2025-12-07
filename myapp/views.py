from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Attendance, Duty
from django.http import JsonResponse
from .models import AdminAccessKey
import secrets
import uuid
from django.shortcuts import render
from .models import AdminProfile
from django.views.decorators.http import require_POST
from django.middleware.csrf import get_token
from datetime import datetime




User = get_user_model()

# ---------------------------
# Registration Views
# ---------------------------
def register_staff(request):
    if request.method == "POST":
        fullname = request.POST.get("fullname")
        email = request.POST.get("email")
        id_no = request.POST.get("id_no")
        selected_role = request.POST.get("role") or "staff"
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register_staff")

        if User.objects.filter(id_number=id_no).exists():
            messages.error(request, "ID number already exists.")
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
        else:
            user = User.objects.create_user(
                id_number=id_no,
                email=email,
                password=password,
                role=selected_role,
                fullname=fullname 
            )
            messages.success(request, "Staff account created successfully! Please log in.")
            return redirect("login")
        
        return redirect("register_staff")

    return render(request, "myapp/register_staff.html")


def register_admin(request):
    if request.method == "POST":
        fullname = request.POST.get("fullname")
        email = request.POST.get("email")
        id_no = request.POST.get("id_no")
        access_code = request.POST.get("access_code")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        key_obj = None
        for k in AdminAccessKey.objects.filter(used=False):
            if k.verify_key(access_code):
                key_obj = k
                break

        if not key_obj:
            messages.error(request, "Invalid or already used admin access key.")
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

        key_obj.used = True
        key_obj.save()

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

        user = authenticate(request, username=id_no, password=password)

        if user is not None:
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

@login_required(login_url="login")
def generate_admin_key(request):
    if request.user.role != "admin":
        messages.error(request, "Access denied.")
        return redirect("home_page")

    if request.method == "POST":
        raw_key = secrets.token_urlsafe(16)  
        key_obj = AdminAccessKey(created_by=request.user)
        key_obj.set_key(raw_key)  
        key_obj.save()

        messages.success(request, f"Admin access key generated: {raw_key}")
        return redirect("admin_dashboard")

    return redirect("admin_dashboard")


# ---------------------------
# Profile Pages
# ---------------------------

@login_required
def admin_profile(request):
    admin = request.user
    profile, created = AdminProfile.objects.get_or_create(
        user=admin,
        defaults={"fullname": getattr(admin, "fullname", "Not Set")}
    )

    context = {
        "admin": admin,
        "profile": profile,
        "user_id": admin.id,
        "csrf_token": get_token(request),  # optional for JS
    }
    return render(request, "myapp/admin_profile.html", context)


@login_required
@require_POST
def update_admin_profile(request):
    # Only admins allowed
    if getattr(request.user, "role", None) != "admin":
        return JsonResponse({"success": False, "message": "Access denied."}, status=403)

    # Get or safely create profile
    try:
        profile = AdminProfile.objects.get(user=request.user)
    except AdminProfile.DoesNotExist:
        profile = AdminProfile(id=uuid.uuid4(), user=request.user)

    # Allowed fields to update
    allowed_fields = [
        "fullname", "dob", "age", "gender", "blood_type", "nationality",
        "phone", "emergency_contact", "address", "work_schedule"
    ]

    for field in allowed_fields:
        if field in request.POST:
            value = request.POST.get(field)

            # DOB
            if field == "dob":
                if value and value.strip():
                    try:
                        profile.dob = datetime.strptime(value, "%Y-%m-%d").date()
                    except ValueError:
                        return JsonResponse({
                            "success": False,
                            "message": "Invalid DOB format, use YYYY-MM-DD"
                        }, status=400)
                else:
                    profile.dob = None

            # Age
            elif field == "age":
                if value and value.strip():
                    try:
                        profile.age = int(value)
                    except ValueError:
                        return JsonResponse({"success": False, "message": "Invalid age"}, status=400)
                else:
                    profile.age = None

            # Phone - must be 11 digits
            elif field == "phone":
                if value and value.strip():
                    # Remove any whitespace
                    phone_clean = value.strip().replace(" ", "").replace("-", "")
                    # Check if it's exactly 11 digits
                    if not phone_clean.isdigit() or len(phone_clean) != 11:
                        return JsonResponse({
                            "success": False,
                            "message": "Phone number must be exactly 11 digits"
                        }, status=400)
                    profile.phone = phone_clean
                else:
                    profile.phone = None

            # Emergency Contact - must be 11 digits
            elif field == "emergency_contact":
                if value and value.strip():
                    # Remove any whitespace
                    contact_clean = value.strip().replace(" ", "").replace("-", "")
                    # Check if it's exactly 11 digits
                    if not contact_clean.isdigit() or len(contact_clean) != 11:
                        return JsonResponse({
                            "success": False,
                            "message": "Emergency contact must be exactly 11 digits"
                        }, status=400)
                    profile.emergency_contact = contact_clean
                else:
                    profile.emergency_contact = None

            # Blood Type - must be valid blood type
            elif field == "blood_type":
                if value and value.strip():
                    valid_blood_types = ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-']
                    blood_type_clean = value.strip().upper()
                    if blood_type_clean not in valid_blood_types:
                        return JsonResponse({
                            "success": False,
                            "message": "Invalid blood type. Valid types: O+, O-, A+, A-, B+, B-, AB+, AB-"
                        }, status=400)
                    profile.blood_type = blood_type_clean
                else:
                    profile.blood_type = None

            # Other fields
            else:
                setattr(profile, field, value if value and value.strip() else None)

    # Save safely
    try:
        profile.save()
    except Exception as e:
        return JsonResponse({"success": False, "message": f"DB save error: {str(e)}"}, status=500)

    return JsonResponse({"success": True, "message": "Profile updated."})




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
    now = timezone.localtime()

    latest = Attendance.objects.filter(user=user).order_by("-check_in").first()

    current_duty = Duty.objects.filter(
        staff=user,
        time_start__lte=now.time(),
        time_end__gte=now.time()
    ).first()

    history = Attendance.objects.filter(user=user).order_by("-check_in")

    context = {
        "latest": latest,
        "history": history,
        "current_duty": current_duty,
        "now": now,
    }

    return render(request, "myapp/attendance_dashboard.html", context)


# ---------------------------
# Admin Views
# ---------------------------
@login_required(login_url="login")
def manage_staff(request):
    if request.user.role != "admin":
        messages.error(request, "Access denied.")
        return redirect("home_page")

    roles = ["security-officer", "supervisor"]

    # Make a list of tuples: (role_name, queryset of staff)
    staff_by_role = []
    for role in roles:
        staff_list = list(User.objects.filter(role=role))  # convert QuerySet to list
        staff_by_role.append((role, staff_list))  # tuple: (role, list_of_staff)

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
        "staff_by_role": staff_by_role,
    }
    return render(request, "myapp/manage_staff.html", context)




# ---------------------------
# Reports Page
# ---------------------------
@login_required(login_url="login")
def reports(request):
    if request.user.role != "admin":
        messages.error(request, "Access denied.")
        return redirect("home_page")

    return render(request, "myapp/reports.html")


# ---------------------------
# Attendance Actions
# ---------------------------
def attendance_action(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method"})

    user = request.user
    action = request.POST.get("action")
    now = timezone.localtime()

    active_shift = Attendance.objects.filter(user=user, check_out__isnull=True).first()

    response = {"success": False, "message": ""}

    if action == "checkin":
        if active_shift:
            response["message"] = "You are already checked in!"
        else:
            record = Attendance.objects.create(user=user, check_in=timezone.now())
            response = {
                "success": True,
                "message": "Check-in successful.",
                "check_in_time": timezone.localtime(record.check_in).strftime("%Y-%m-%d %H:%M:%S")
            }

    elif action == "checkout":
        if not active_shift:
            response["message"] = "You have no active check-in to check out from."
        else:
            active_shift.check_out = timezone.now()
            active_shift.save()
            response = {
                "success": True,
                "message": "Check-out successful.",
                "check_out_time": timezone.localtime(active_shift.check_out).strftime("%Y-%m-%d %H:%M:%S")
            }

    else:
        response["message"] = "Invalid action."

    return JsonResponse(response)


@login_required(login_url="login")
def remove_duty(request, duty_id):
    if request.user.role != "admin":
        messages.error(request, "Access denied.")
        return redirect("home_page")

    duty = get_object_or_404(Duty, id=duty_id)
    duty.delete()
    messages.success(request, "Duty removed successfully.")
    return redirect("manage_staff")


@login_required(login_url="login")
def edit_duty(request, duty_id):
    if request.user.role != "admin":
        messages.error(request, "Access denied.")
        return redirect("home_page")

    duty = get_object_or_404(Duty, id=duty_id)

    if request.method == "POST":
        duty.location = request.POST.get("location")
        duty.status = request.POST.get("status")
        duty.save()
        messages.success(request, "Duty updated successfully.")
        return redirect("manage_staff")

    context = {"duty": duty}
    return render(request, "myapp/edit_duty.html", context)
