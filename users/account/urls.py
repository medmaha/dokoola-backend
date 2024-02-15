from django.urls import path
from . import login
from . import signup
from . import verify
from . import logout


urlpatterns = [
    path("login", login.LoginView.as_view(), name="login"),
    path("signup", signup.SignUpView.as_view(), name="signup"),
    path("verify", verify.verifyEmail, name="verify"),
    path("logout", logout.LogoutView.as_view(), name="logout"),
    path("signup/check", signup.check_email, name="check_email"),
    path("info", signup.SignupUserInformation.as_view(), name="signup"),
]
