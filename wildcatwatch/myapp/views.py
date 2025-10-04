from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password

# Optional: create a simple UserProfile model in models.py
# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     idnumber = models.CharField(max_length=50, unique=True)
#     role = models.CharField(max_length=50)

def register(request):
    if request.method == "POST":
        fullname = request.POST.get("fullname")      # Full Name
        email = request.POST.get("email")            # Email
        idnumber = request.POST.get("idnumber")      # ID Number
        role = request.POST.get("role")              # Role
        password = request.POST.get("password")      # Password
        confirm_password = request.POST.get("confirm_password")  # Confirm Password

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, "myapp/register.html")

        # Check if email or idnumber already exists
        if User.objects.filter(username=idnumber).exists():
            messages.error(request, "ID number already registered!")
            return render(request, "myapp/register.html")
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return render(request, "myapp/register.html")

        # Create user using idnumber as username
        user = User.objects.create(
            username=idnumber,                    # Use ID as username
            email=email,
            password=make_password(password),     # Hash the password
            first_name=fullname.split()[0],
            last_name=" ".join(fullname.split()[1:]) if len(fullname.split()) > 1 else ""
        )

        # Optional: save role in a profile model
        # UserProfile.objects.create(user=user, idnumber=idnumber, role=role)

        messages.success(request, "User registered successfully! You can now log in.")
        return redirect("login")

    return render(request, "myapp/register.html")


def login_view(request):
    if request.method == "POST":
        idnumber = request.POST.get("idnumber")   # ID number used as username
        password = request.POST.get("password")
        role = request.POST.get("role")

        try:
            user = User.objects.get(username=idnumber)
        except User.DoesNotExist:
            messages.error(request, "Invalid ID number or password")
            return render(request, "myapp/login.html")

        if check_password(password, user.password):
            # Login successful
            request.session['user_id'] = user.id
            request.session['role'] = role

            # Role-based redirection
            if role == "administrator":
                return redirect("admin_dashboard")
            elif role == "security-guard":
                return redirect("staff_dashboard")
            else:
                return redirect("home_page_root")
        else:
            messages.error(request, "Invalid ID number or password")
            return render(request, "myapp/login.html")

    return render(request, "myapp/login.html")


def home_page(request):
    return render(request, "myapp/home_page.html")
