from django.urls import path
from . import login
from . import signup
from . import verify
from . import logout


urlpatterns = [
    path("login", login.LoginView.as_view(), name="login"),
    path("verify", verify.verifyEmail, name="verify"),
    path("logout", logout.LogoutView.as_view(), name="logout"),
    path("signup/", signup.SignUpView.as_view(), name="signup"),
    path("signup/mail-check/", signup.CheckEmailView.as_view(), name="check_email"),
    path("signup/mail-resend/", signup.ResendCodeView.as_view(), name="resend_code"),
    path("signup/mail-verify/", signup.VerifyCodeView.as_view(), name="verify_code"),
    path("info/", signup.SignupUserInformation.as_view(), name="signup"),
]
