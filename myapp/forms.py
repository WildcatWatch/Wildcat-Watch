from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            fullname = form.cleaned_data["fullname"]
            email = form.cleaned_data["email"].lower()
            id_no = form.cleaned_data["id_no"]
            role = form.cleaned_data["role"]
            password = form.cleaned_data["password"]

            if User.objects.filter(username=id_no).exists():
                form.add_error("id_no", "ID number already exists")
                return render(request, "myapp/register.html", {"form": form})

            user = User.objects.create_user(username=id_no, email=email, password=password)
            user.first_name = fullname
            user.last_name = role  
            user.save()

            messages.success(request, "Account created successfully! Please log in.")
            return redirect("login")
        else:
            return render(request, "myapp/register.html", {"form": form})
    else:
        form = RegisterForm()

    return render(request, "myapp/register.html", {"form": form})
