from django.urls import path
from . import views
#imports for forgotten password
from django.contrib.auth.views import (
    LogoutView, 
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView,
    PasswordResetCompleteView
)

app_name='customer'
urlpatterns=[
    path('',views.registerView,name='register'),
    path('otp/<int:id>', views.verifyOtp, name='otp'),
    path("resend_otp/<int:id>",views.resendOtp,name='resend_otp'),    
    path("login/",views.login_view,name='login'),
    path("logout/",views.logout_view,name='logout'),
    path("profile/",views.profile_view,name='profile'),
    path("change_password/",views.change_password_view,name='change_password'),
    path("edit_profile/",views.edit_profile_view,name='edit_profile'),
    path("add_new_address/<str:source>",views.add_new_address,name='add_new_address'),
    path("edit_address/<int:id>",views.edit_address,name='edit_address'),
    path("delete_address/<int:id>",views.delete_address,name='delete_address'),
    path("check_username/",views.check_username,name='check_username'),
    path('validate_password/',views.validate_passwords_view,name='validate_passwords'),
    path('test_register/',views.test_register,name='test_register'),
    path('create_referral_link/',views.create_referral_link,name='create_referral_link'),
    

]