from django.urls import path
from . import views 

urlpatterns = [
    path("", views.register, name='register_root'),
    path("register/", views.register, name='register'),
    path("login/", views.login_view, name='login'),
    path("home_page/", views.home_page, name='home_page'),
]
