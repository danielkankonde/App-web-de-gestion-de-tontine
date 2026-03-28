from django.urls import path
from .views import forgot_password_view, login_view, register_view, reset_password_view, reset_verify_view, verify_view, resend_code_view
urlpatterns = [
    path("login/", login_view, name='login'),
    path("register/", register_view, name='register'),
    path("verify/", verify_view, name='verify'),

    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('verify-reset-password/', reset_verify_view, name='reset_verify'),
    path('reset-password/', reset_password_view, name='reset_password'),

    path('resend-code/', resend_code_view, name='resend_code'),
]
