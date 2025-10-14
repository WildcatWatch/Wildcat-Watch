from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == "POST":
        fullname = request.POST.get("fullname")
        email = request.POST.get("email")
        id_no = request.POST.get("id_no")
        role = request.POST.get("role")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Basic validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")
        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
            return redirect("register")
        if not email.endswith("@cit.edu"):
            messages.error(request, "Email must be a valid @cit.edu address.")
            return redirect("register")
        if User.objects.filter(username=id_no).exists():
            messages.error(request, "ID number already exists.")
            return redirect("register")

        # Create user and store role
        user = User.objects.create_user(username=id_no, email=email, password=password)
        user.first_name = fullname
        user.last_name = role  # 🔹 store role here
        user.save()

        messages.success(request, "Account created successfully! Please log in.")
        return redirect("login")

    return render(request, "myapp/register.html")


def login_view(request):
    if request.method == "POST":
        id_no = request.POST.get("id_no")
        password = request.POST.get("password")
        selected_role = request.POST.get("role")

        user = authenticate(request, username=id_no, password=password)

        if user is not None:
            if user.last_name != selected_role:
                messages.error(request, "Invalid role selected for this account.")
                return redirect("login")

            login(request, user)

            # Redirect based on stored role
            if user.last_name == "administrator":
                return redirect("admin_dashboard")
            elif user.last_name in ["security-officer", "supervisor"]:
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

#added
@login_required(login_url="login")
def staff_dashboard(request):
    return render(request, "myapp/staff_dashboard.html")

@login_required(login_url="login")
def admin_dashboard(request):
    return render(request, "myapp/admin_dashboard.html")
