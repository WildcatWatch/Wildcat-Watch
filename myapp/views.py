from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Attendance, Duty, AdminAccessKey, Notification
from django.http import JsonResponse
import secrets
from datetime import timedelta
from django.db.models import Count
from .models import AdminProfile
from django.views.decorators.http import require_POST
from django.middleware.csrf import get_token
from datetime import datetime
from .models import StaffProfile
from django.utils import timezone
from django.db.models import Q



User = get_user_model()

# ---------------------------
# Registration Views
# ---------------------------
def register_staff(request):
    if request.method == "POST":
        fullname = request.POST.get("fullname")
        email = request.POST.get("email")
        id_no = request.POST.get("id_no")
        selected_role = request.POST.get("role")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if selected_role not in ['security', 'janitor']:
            messages.error(request, "Invalid role selected.")
            return redirect("register_staff")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register_staff")

        if User.objects.filter(id_number=id_no).exists():
            messages.error(request, "ID number already exists.")
            return redirect("register_staff")
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("register_staff")
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
            elif user.role in ["security", "janitor"]:
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
    user = request.user
    
    unread_notifications = Notification.objects.filter(user=user, is_read=False)

    context = {
        'staff': user, 
        'unread_notifications': unread_notifications, 
    }
    
    return render(request, "myapp/staff_dashboard.html", context)


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
# Employee Views - my_duties_view 
# ---------------------------
@login_required(login_url="login")
def my_duties_view(request):
    duties = Duty.objects.filter(staff=request.user).order_by('time_start')

    if request.method == "POST":
        duty_id = request.POST.get("duty_id")
        new_status = request.POST.get("status", "completed") 
        
        duty = get_object_or_404(Duty, id=duty_id, staff=request.user)
        
        if new_status in ["completed", "ongoing", "pending"]:
            duty.status = new_status
            duty.save()
            messages.success(request, f"Duty **{duty.title}** status updated to {new_status.capitalize()}.")
        else:
            messages.error(request, "Invalid status submitted.")
            
        return redirect("my_duties")

    return render(request, "myapp/my_duties.html", {"duties": duties})


# ---------------------------
# Employee Views - attendance_dashboard 
# ---------------------------
@login_required(login_url="login")
def attendance_dashboard(request):
    user = request.user
    now = timezone.localtime()

    latest = Attendance.objects.filter(user=user).order_by("-check_in").first()

    current_duty = Duty.objects.filter(
        staff=user,
        time_start__lte=now,
        time_end__gt=now 
    ).first()

    history = Attendance.objects.filter(user=user).order_by("-check_in")

    context = {
        "latest": latest,
        "history": history,
        "current_duty": current_duty,
        "now": now,
    }

    return render(request, "myapp/attendance_dashboard.html", context)


@login_required(login_url="login")
def manage_staff(request):
    if request.user.role != "admin":
        messages.error(request, "Access denied.")
        return redirect("home_page")

    staff_list = User.objects.filter(role__in=["security", "janitor"]) 
    duty_list = Duty.objects.all().order_by("-time_start") 

    if request.method == "POST":
        action_type = request.POST.get("action_type") 
        
        if action_type == "delete":
            duty_id = request.POST.get("duty_id")
            duty = get_object_or_404(Duty, id=duty_id)
            
            if duty:
                duty_title = duty.title
                duty.delete()
                messages.success(request, f"Duty '{duty_title}' successfully deleted.")
                return redirect("manage_staff")
        
        duty_id = request.POST.get("duty_id") 
        staff_id = request.POST.get("staff_id_input") 
        duty_title = request.POST.get("titleInput")
        place = request.POST.get("placeInput")
        description = request.POST.get("descriptionInput")
        time_start_str = request.POST.get("timeStartInput")
        time_end_str = request.POST.get("timeEndInput")
        
        try:
            staff_member = User.objects.get(id=staff_id)
            
            DATETIME_INPUT_FORMAT = '%Y-%m-%dT%H:%M'

            if not time_start_str or not time_end_str:
                messages.error(request, "Start time and End time are required.")
                return redirect("manage_staff")
            
            time_start = timezone.datetime.strptime(time_start_str, DATETIME_INPUT_FORMAT).astimezone(timezone.get_current_timezone())
            time_end = timezone.datetime.strptime(time_end_str, DATETIME_INPUT_FORMAT).astimezone(timezone.get_current_timezone())
            
            if time_start >= time_end:
                messages.error(request, "Duty end time must be after start time.")
                return redirect("manage_staff")

            overlap_query = Duty.objects.filter(
                staff=staff_member,
                time_start__lt=time_end, 
                time_end__gt=time_start,
            )
            
            if action_type == "update" and duty_id:
                overlap_query = overlap_query.exclude(id=duty_id)
                
            if overlap_query.exists():
                messages.error(request, f"Duty assignment conflicts with an existing duty for {staff_member.fullname} during that period.")
                return redirect("manage_staff")

            duty_data = {
                "staff": staff_member,
                "title": duty_title,
                "location": place,
                "description": description,
                "time_start": time_start,
                "time_end": time_end,
            }
            
            if action_type == "create":
                Duty.objects.create(**duty_data, status="pending")
                messages.success(request, f"Duty assigned to {staff_member.fullname} successfully.")
                
            elif action_type == "update" and duty_id:
                duty_instance = get_object_or_404(Duty, id=duty_id)
                
                for key, value in duty_data.items():
                    setattr(duty_instance, key, value)
                duty_instance.save()
                
                messages.success(request, f"Duty '{duty_title}' successfully updated.")
                
            else:
                messages.error(request, "Invalid action or missing ID for update.")

        except User.DoesNotExist:
            messages.error(request, "Staff member not found.")
        except ValueError:
            messages.error(request, "Invalid date/time format submitted. Ensure format is YYYY-MM-DD HH:MM:SS.")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred during operation.")
            
        return redirect("manage_staff")

    context = {
        "staff_list": staff_list,
        "duty_list": duty_list
    }
    return render(request, "myapp/manage_staff.html", context)


# ---------------------------
# Reports Views
# ---------------------------
@login_required(login_url="login")
def reports(request):
    if request.user.role != "admin":
        messages.error(request, "Access denied.")
        return redirect("home_page")

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    staff_role = request.GET.get('staff_role')
    
    report_data = Attendance.objects.none()
    total_records = 0
    completed_duties = 0
    missed_duties = 0

    if start_date_str or end_date_str or staff_role:
        
        report_data = Attendance.objects.select_related('user', 'assigned_duty').all().order_by('-check_in')

        try:
            if start_date_str:
                start_datetime = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
                report_data = report_data.filter(check_in__date__gte=start_datetime)
                
            if end_date_str:
                end_datetime = timezone.datetime.strptime(end_date_str, '%Y-%m-%d').date()
                end_of_day = end_datetime + timedelta(days=1)
                report_data = report_data.filter(check_in__date__lt=end_of_day)

            if staff_role and staff_role != 'all' and staff_role in ['security', 'janitor', 'admin']:
                report_data = report_data.filter(user__role=staff_role)

            total_records = report_data.count()
            
            completed_duties = report_data.filter(
                assigned_duty__status='completed'
            ).aggregate(count=Count('assigned_duty', distinct=True))['count'] or 0

            missed_duties = report_data.filter(
                assigned_duty__status='missed'
            ).aggregate(count=Count('assigned_duty', distinct=True))['count'] or 0
            
        except ValueError:
            messages.error(request, "Invalid date format provided. Please use YYYY-MM-DD.")
            report_data = Attendance.objects.none() 

    context = {
        'report_records': report_data,
        'total_records': total_records,
        'completed_duties': completed_duties,
        'missed_duties': missed_duties,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'staff_role': staff_role,
    }
    
    return render(request, 'myapp/reports.html', context)


# ---------------------------
# Employee Views - check_in
# ---------------------------
@login_required
def check_in(request):
    user = request.user
    now = timezone.localtime() 

    active_shift = Attendance.objects.filter(user=user, check_out__isnull=True).first()
    if active_shift:
        messages.error(request, "You are already checked in! Check out first.")
        return redirect("attendance_dashboard")

    current_duty = Duty.objects.filter(
        staff=user,
        time_start__lte=now,
        time_end__gt=now, 
        status__in=['pending', 'ongoing']
    ).first()
    
    Attendance.objects.create(
        user=user,
        check_in=timezone.now(),
        assigned_duty=current_duty 
    )

    if current_duty:
        current_duty.status = 'ongoing'
        current_duty.save()
        messages.success(request, f"Checked in successfully. Your shift is **{current_duty.title}**.")
    else:
        messages.warning(request, "Checked in successfully. No scheduled duty found for this exact time.")

    return redirect("attendance_dashboard")


# ---------------------------
# Employee Views - check_out 
# ---------------------------
@login_required
def check_out(request):
    user = request.user
    active_shift = Attendance.objects.filter(user=user, check_out__isnull=True).first()

    if not active_shift:
        messages.error(request, "You have no active shift to check out.")
        return redirect("attendance_dashboard")

    checkout_time = timezone.now()
    active_shift.check_out = checkout_time
    active_shift.save()

    if active_shift.assigned_duty:
        duty = active_shift.assigned_duty
        
        early_tolerance = timedelta(minutes=15)
        
        compliant_checkout_time = duty.time_end - early_tolerance
        
        if checkout_time < compliant_checkout_time:
            duty.status = 'missed' 
            messages.warning(request, f"Checked out successfully. Duty **{duty.title}** was marked as **MISSED** due to early departure.")
        else:
            duty.status = 'completed'
            messages.success(request, f"Checked out successfully, and duty **{duty.title}** marked as completed.")
            
        duty.save()
    else:
        messages.success(request, "Checked out successfully (Unscheduled attendance recorded).")

    return redirect("attendance_dashboard")


# ---------------------------
# JSON API Check-in/out View
# ---------------------------
@login_required
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
            current_duty = Duty.objects.filter(
                staff=user,
                time_start__lte=now,
                time_end__gt=now,
                status__in=['pending', 'ongoing']
            ).first()
            
            record = Attendance.objects.create(
                user=user, 
                check_in=timezone.now(),
                assigned_duty=current_duty
            )
            
            if current_duty:
                current_duty.status = 'ongoing'
                current_duty.save()
                
            response = {
                "success": True,
                "message": f"Check-in successful. Duty: {current_duty.title}" if current_duty else "Check-in successful.",
                "check_in_time": timezone.localtime(record.check_in).strftime("%Y-%m-%d %H:%M:%S")
            }

    elif action == "checkout":
        if not active_shift:
            response["message"] = "You have no active check-in to check out from."
        else:
            checkout_time = timezone.now()
            active_shift.check_out = checkout_time
            
            if active_shift.assigned_duty:
                duty = active_shift.assigned_duty
                early_tolerance = timedelta(minutes=15)
                compliant_checkout_time = duty.time_end - early_tolerance
                
                if checkout_time < compliant_checkout_time:
                    duty.status = 'missed' 
                else:
                    duty.status = 'completed'
                
                duty.save()
            
            active_shift.save()
            
            response = {
                "success": True,
                "message": "Check-out successful.",
                "check_out_time": timezone.localtime(active_shift.check_out).strftime("%Y-%m-%d %H:%M:%S")
            }

    else:
        response["message"] = "Invalid action."

    return JsonResponse(response)


# ---------------------------
# Notification View
# ---------------------------
@login_required(login_url="login")
def notifications_list(request):
    notifications = Notification.objects.filter(user=request.user) 
    
    notifications.filter(is_read=False).update(is_read=True)
    
    context = {
        'notifications': notifications
    }
    return render(request, 'myapp/notifications.html', context)

@login_required(login_url="login")
def staff_profile(request):
    # Only staff (security/janitor) can access this page
    if request.user.role not in ["security", "janitor"]:
        return redirect("admin_profile")

    # Get or create staff profile
    profile, created = StaffProfile.objects.get_or_create(
        user_id=request.user.id,
        defaults={
            "fullname": getattr(request.user, "fullname", "Not Set"),
            "role": request.user.role
        }
    )

    context = {
        "staff": request.user,
        "profile": profile
    }

    return render(request, "myapp/staff_profile.html", context)


@login_required(login_url="login")
def admin_profile(request):
    # Only admins can access this page
    if request.user.role != "admin":
        return redirect("staff_profile")
    
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

    # Allowed fields (updated)
    allowed_fields = [
        "fullname", "dob", "age", "gender",
        "user_id", "email",         # UPDATED FIELDS
        "phone", "emergency_contact",
        "address", "work_schedule"
    ]

    for field in allowed_fields:
        if field in request.POST:
            value = request.POST.get(field).strip()

            # --- DOB ---
            if field == "dob":
                if value:
                    try:
                        profile.dob = datetime.strptime(value, "%Y-%m-%d").date()
                    except ValueError:
                        return JsonResponse({
                            "success": False,
                            "message": "Invalid DOB format, use YYYY-MM-DD"
                        }, status=400)
                else:
                    profile.dob = None

            # --- AGE ---
            elif field == "age":
                if value:
                    try:
                        profile.age = int(value)
                    except ValueError:
                        return JsonResponse({
                            "success": False,
                            "message": "Age must be a number"
                        }, status=400)
                else:
                    profile.age = None

            # --- PHONE (11 digits) ---
            elif field == "phone":
                phone_clean = value.replace(" ", "").replace("-", "")
                if phone_clean and (not phone_clean.isdigit() or len(phone_clean) != 11):
                    return JsonResponse({
                        "success": False,
                        "message": "Phone number must be exactly 11 digits"
                    }, status=400)
                profile.phone = phone_clean or None

            # --- EMERGENCY CONTACT (11 digits) ---
            elif field == "emergency_contact":
                contact_clean = value.replace(" ", "").replace("-", "")
                if contact_clean and (not contact_clean.isdigit() or len(contact_clean) != 11):
                    return JsonResponse({
                        "success": False,
                        "message": "Emergency contact must be exactly 11 digits"
                    }, status=400)
                profile.emergency_contact = contact_clean or None

            # --- USER ID (INT4) ---
            elif field == "user_id":
                if value:
                    if not value.isdigit():
                        return JsonResponse({
                            "success": False,
                            "message": "User ID must be an integer"
                        }, status=400)
                    profile.user_id = int(value)
                else:
                    profile.user_id = None

            # --- EMAIL ---
            elif field == "email":
                if value:

                    if "@" not in value or "." not in value:

                        return JsonResponse({

                            "success": False,
                            "message": "Invalid email format"
                        }, status=400)
                profile.email = value or None
                # Update actual User model as well
                request.user.email = value or None
                request.user.save()


            # --- OTHER FIELDS ---
            else:
                setattr(profile, field, value or None)

    # Save safely
    try:
        profile.save()
    except Exception as e:
        return JsonResponse({"success": False, "message": f"DB save error: {str(e)}"}, status=500)

    # Return all updated fields so frontend can update dynamically
    return JsonResponse({
        "success": True,
        "message": "Profile updated.",
        "fullname": profile.fullname,
        "dob": profile.dob.strftime("%Y-%m-%d") if profile.dob else '',
        "age": profile.age,
        "gender": profile.gender,
        "phone": profile.phone,
        "emergency_contact": profile.emergency_contact,
        "address": profile.address,
        "email": profile.email
    })



@login_required
@require_POST
def update_staff_profile(request):
    # Only staff allowed
    if getattr(request.user, "role", None) not in ["security", "janitor"]:
        return JsonResponse({"success": False, "message": "Access denied."}, status=403)

    # Get or create profile
    profile, created = StaffProfile.objects.get_or_create(user=request.user)

    allowed_fields = [
        "fullname", "dob", "age", "gender", "blood_type", "nationality",
        "phone", "emergency_contact", "address",
        "staff_id", "work_schedule", "role", "user_id", "email"
    ]

    for field in allowed_fields:
        if field in request.POST:
            value = request.POST.get(field)

            # --- DATE OF BIRTH ---
            if field == "dob":
                profile.dob = datetime.strptime(value, "%Y-%m-%d").date() if value else None

            # --- AGE ---
            elif field == "age":
                profile.age = int(value) if value else None

            # --- PHONE ---
            elif field == "phone":
                clean = value.replace(" ", "").replace("-", "") if value else None
                if clean and (not clean.isdigit() or len(clean) != 11):
                    return JsonResponse({"success": False, "message": "Phone must be 11 digits"}, status=400)
                profile.phone = clean

            # --- EMERGENCY CONTACT ---
            elif field == "emergency_contact":
                clean = value.replace(" ", "").replace("-", "") if value else None
                if clean and (not clean.isdigit() or len(clean) != 11):
                    return JsonResponse({"success": False, "message": "Emergency contact must be 11 digits"}, status=400)
                profile.emergency_contact = clean

            # --- BLOOD TYPE ---
            elif field == "blood_type":
                valid_blood_types = ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-']
                bt = value.strip().upper() if value else None
                if bt and bt not in valid_blood_types:
                    return JsonResponse({"success": False, "message": "Invalid blood type"}, status=400)
                profile.blood_type = bt

            # --- USER ID ---
            elif field == "user_id":
                if value:
                    if not value.isdigit():
                        return JsonResponse({
                            "success": False,
                            "message": "User ID must be an integer"
                        }, status=400)
                    profile.user_id = int(value)
                else:
                    profile.user_id = None

            # --- EMAIL ---
            elif field == "email":
                if value:
                    if "@" not in value or "." not in value:
                        return JsonResponse({
                            "success": False,
                            "message": "Invalid email format"
                        }, status=400)
                profile.email = value or None
                # Update actual User model as well
                request.user.email = value or None
                request.user.save()

            # --- OTHER FIELDS ---
            else:
                setattr(profile, field, value if value else None)

    # Save
    profile.save()
    return JsonResponse({"success": True, "message": "Staff profile updated successfully."})


@login_required
def mark_notification_read(request):
    if request.method == 'POST':
        notif_id = request.POST.get('id')
        notif = get_object_or_404(Notification, id=notif_id, user=request.user)
        notif.is_read = True
        notif.save()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def mark_all_notifications_read(request):
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def delete_notification(request):
    if request.method == 'POST':
        notif_id = request.POST.get('id')
        notif = get_object_or_404(Notification, id=notif_id, user=request.user)
        notif.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)

    


@login_required(login_url="login")
def admin_dashboard(request):
    # Only allow admins
    if request.user.role != "admin":
        messages.error(request, "Access denied.")
        return redirect("home_page")

    now = timezone.localtime()
    today = now.date()

    # Total staff (security + janitor)
    total_staff = User.objects.filter(role__in=["security", "janitor"]).count()

    # Duties today
    duties_today = Duty.objects.filter(time_start__date=today)
    pending_duties = duties_today.filter(status="pending").count()
    completed_duties = duties_today.filter(status="completed").count()
    missing_duties = duties_today.filter(status="missed").count()

    # Staff currently on duty
    staff_on_duty_now = []
    active_duties = Duty.objects.filter(
        time_start__lte=now,
        time_end__gte=now,
        status__in=["pending", "ongoing"]
    ).select_related('staff')

    for duty in active_duties:
        staff_on_duty_now.append({
            "fullname": duty.staff.fullname,
            "current_location": duty.location,
            "shift_start": duty.time_start.strftime("%H:%M"),
        })

    context = {
        "total_staff": total_staff,
        "pending_duties": pending_duties,
        "completed_duties": completed_duties,
        "missing_duties": missing_duties,
        "staff_on_duty_now": staff_on_duty_now,
    }

    return render(request, "myapp/admin_dashboard.html", context)

