from django.shortcuts import render

# Create your views here.
#backend

def register(request):
    return render(request, "myapp/register.html")

def login_view(request):
    return render(request, "myapp/login.html")

def home_page(request):
    return render(request, "myapp/home_page.html")