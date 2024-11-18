from django.urls import path
from api.errors import error_json
from ..views import authViews


urlpatterns = [
    path(
        "email/checkavailability/",
        authViews.CheckEmailAvailable.as_view(),
        name="checkEmailAvailable",
    ),
    path("email/sendotp/", authViews.SendEmailOTP.as_view(), name="sendOTP"),
    path("email/verifyotp/", authViews.VerifyEmailOTP.as_view(), name="verifyOTP"),
    path("createuser/", authViews.CreateUserView.as_view(), name="createUser"),
    path("login/", authViews.LoginView.as_view(), name="login"),
    path("validate/", authViews.ValidateLoginView.as_view(), name="test_login"),
    path("logout/", authViews.logoutUser, name="logout"),
    path("invalid_login/", authViews.invalidLogin, name="invalid_login"),
    path(
        "password/reset", authViews.ResetPasswordView.as_view(), name="reset_password"
    ),
    # path("password/forgot/"),
    path(
        "password/forgot/otp/",
        authViews.PasswordResetOTPEmail.as_view(),
        name="password_forgot_otp",
    ),
    path(
        "password/forgot/reset/",
        authViews.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("user/", authViews.UserDetailsView.as_view(), name="user_details"),
]
