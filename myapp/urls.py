from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('login/', views.login_view, name='login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('my-duties/', views.my_duties_view, name='my_duties'),
    path('attendance/', views.attendance_dashboard, name='attendance_dashboard'),
    path('attendance/action/', views.attendance_action, name='attendance_action'),
    path('register/staff/', views.register_staff, name='register_staff'),
    path('register/admin/', views.register_admin, name='register_admin'),
    path('manage-staff/', views.manage_staff, name='manage_staff'),
    path('reports/', views.reports, name='reports'),
    path('generate-admin-key/', views.generate_admin_key, name='generate_admin_key'),
    path('staff-profile/', views.staff_profile, name='staff_profile'),
    path('admin-profile/', views.admin_profile, name='admin_profile'),
    path("admin_profile/edit_personal/", views.edit_admin_personal_info, name="edit_admin_personal_info"),
    path("admin_profile/edit_contact/", views.edit_admin_contact_info, name="edit_admin_contact_info"),
    path("admin_profile/edit_employment/", views.edit_admin_employment_info, name="edit_admin_employment_info"),
    path("admin_profile/edit_security/", views.edit_admin_account_security, name="edit_admin_account_security"),


]


