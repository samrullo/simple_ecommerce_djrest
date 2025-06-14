"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from api.views import CustomJWTLoginView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


from ecommerce.viewsets.user.viewsets import (
    CustomVerifyEmailView,
    CustomRegisterView,
    CustomLoginView,
    ResendEmailVerificationView,
    get_user_info,
)
from django.contrib.auth import views as auth_views

# urls.py (development only)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ecommerce/", include("ecommerce.urls")),
    path("api/", include("api.urls")),
    path("auth/login/", CustomLoginView.as_view(), name="rest_login"),
    path("auth/", include("dj_rest_auth.urls")),  # Login, Logout, Password Reset
    path(
        "auth/registration/account-confirm-email/<str:key>/",
        CustomVerifyEmailView.as_view(),
        name="account_confirm_email",
    ),
    # this is the path that React component Register.js is using to register a new user
    path("auth/register/", CustomRegisterView.as_view(), name="rest_register"),
    # this is the path that EmailNotVerified.js is using to resend email verification
    path(
        "auth/resend-email-verification/",
        ResendEmailVerificationView.as_view(),
        name="resend-email-verification",
    ),
    path("auth/registration/", include("dj_rest_auth.registration.urls")),
    # Registration + Email Verification
    path("auth/user-info/", get_user_info, name="user-info"),
    # This is needed for `password_reset_confirm` reverse lookup
    path(
        "auth/password/reset/confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
