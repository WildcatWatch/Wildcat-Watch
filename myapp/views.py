from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

def register(request):
    if request.method == "POST":
        fullname = request.POST.get("fullname")
        email = request.POST.get("email")
        id_no = request.POST.get("id_no")
        role = request.POST.get("role")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, "myapp/register.html", {
                "form": {
                    "fullname": fullname,
                    "email": email,
                    "id_no": id_no,
                    "role": role
                }
            })

        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long")
            return render(request, "myapp/register.html", {
                "form": {
                    "fullname": fullname,
                    "email": email,
                    "id_no": id_no,
                    "role": role
                }
            })

        if not email.endswith("@cit.edu"):
            messages.error(request, "Email must be a valid @cit.edu address")
            return render(request, "myapp/register.html", {
                "form": {
                    "fullname": fullname,
                    "email": email,
                    "id_no": id_no,
                    "role": role
                }
            })

        if User.objects.filter(username=id_no).exists():
            messages.error(request, "ID number already exists")
            return render(request, "myapp/register.html", {
                "form": {
                    "fullname": fullname,
                    "email": email,
                    "id_no": id_no,
                    "role": role
                }
            })

        user = User.objects.create_user(username=id_no, email=email, password=password)
        user.first_name = fullname
        user.save()
        messages.success(request, "Account created successfully! Please log in.")
        return redirect("login")

    return render(request, "myapp/register.html")

def login_view(request):
    if request.method == "POST":
        id_no = request.POST.get("id_no") 
        password = request.POST.get("password")

        user = authenticate(request, username=id_no, password=password)

        if user is not None:
            login(request, user)
            return redirect("home_page")
        else:
            messages.error(request, "Invalid ID number or password")
            return redirect("login")

    return render(request, "myapp/login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

def home_page(request):
    return render(request, "myapp/home_page.html")
