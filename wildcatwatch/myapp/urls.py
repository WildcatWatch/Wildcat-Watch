from django.urls import path
from . import views 

urlpatterns = [
    path("", views.home_page, name='home_page_root'),  # 👈 root goes to home_page now
    path("register/", views.register, name='register'),
    path("login/", views.login_view, name='login'),
    path("home_page/", views.home_page, name='home_page'),
]
