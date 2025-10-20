from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required

User = get_user_model()

#def register(request):
#    if request.method == "POST":
#        fullname = request.POST.get("fullname")
#        email = request.POST.get("email")
#        id_no = request.POST.get("id_no")
#        role = request.POST.get("role")
#        password = request.POST.get("password")
#        confirm_password = request.POST.get("confirm_password")

        # Basic validation
#        if password != confirm_password:
#            messages.error(request, "Passwords do not match.")
#            return redirect("register")
#        if len(password) < 6:
#            messages.error(request, "Password must be at least 6 characters long.")
#            return redirect("register")
#        if not email.endswith("@cit.edu"):
#            messages.error(request, "Email must be a valid @cit.edu address.")
#            return redirect("register")
#        if User.objects.filter(username=id_no).exists():
#            messages.error(request, "ID number already exists.")
#            return redirect("register")

        # Create user and store role
#        user = User.objects.create_user(username=id_no, email=email, password=password)
#        user.first_name = fullname
#        user.last_name = role  # 🔹 store role here
#        user.save()

#        messages.success(request, "Account created successfully! Please log in.")
#        return redirect("login")

#    return render(request, "myapp/register.html")


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


#def login_view(request):
#    if request.method == "POST":
#        id_no = request.POST.get("id_no")
#        password = request.POST.get("password")
#        selected_role = request.POST.get("role")

#        user = authenticate(request, username=id_no, password=password)

#        if user is not None:
#            if user.last_name != selected_role:
#                messages.error(request, "Invalid role selected for this account.")
#                return redirect("login")

#            login(request, user)

            # Redirect based on stored role
#            if user.last_name == "administrator":
#                return redirect("admin_dashboard")
#            elif user.last_name in ["security-officer", "supervisor"]:
#                return redirect("staff_dashboard")
#            else:
#                return redirect("home_page")
#        else:
#            messages.error(request, "Invalid ID number or password.")
#           return redirect("login")

#    return render(request, "myapp/login.html")


def login_view(request):
    if request.method == "POST":
        id_no = request.POST.get("id_no")
        password = request.POST.get("password")
        role = request.POST.get("role")

        user = authenticate(request, id_number=id_no, password=password)

        if user is not None:
            if user.role != role:
                messages.error(request, "Invalid role selected for this account.")
                return redirect("login")

            login(request, user)

            if user.role == "admin":
                return redirect("admin_dashboard")
            elif user.role in ["security", "supervisor"]:
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


def home_page(request):
    return render(request, "myapp/home_page.html")

@login_required(login_url="login")
def staff_dashboard(request):
    return render(request, "myapp/staff_dashboard.html")

@login_required(login_url="login")
def admin_dashboard(request):
    return render(request, "myapp/admin_dashboard.html")
