from django.urls import path

from . import (
    login,
    logout,
    profile,
    signup,
    signup_check_email,
    signup_extra_info,
    signup_resend_ott,
    signup_verify_ott,
)

# Reference -> /api/account/*/**/
urlpatterns = [
    path("login/", login.LoginView.as_view(), name="login"),
    path(
        "verify",
        signup_verify_ott.VerifyOttAPIView.as_view(),
        name="verify",
    ),
    path("logout/", logout.LogoutView.as_view(), name="logout"),
    path("signup/", signup.SignupAPIView.as_view(), name="signup"),
    path(
        "signup/mail-check/",
        signup_check_email.SignupCheckEmailAPIView.as_view(),
        name="check_email",
    ),
    path(
        "signup/mail-resend/",
        signup_resend_ott.ResendOttAPIView.as_view(),
        name="resend_code",
    ),
    path(
        "signup/mail-verify/",
        signup_verify_ott.VerifyOttAPIView.as_view(),
        name="verify_code",
    ),
    path(
        "info/",
        signup_extra_info.UserProfileUpdateAPIView.as_view(),
        name="signup-info",
    ),
    path(
        "at/<username>/",
        profile.UserProfileAPIView.as_view(),
        name="profile",
    ),
]
