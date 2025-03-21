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
from ecommerce.viewsets.user.viewsets import CustomVerifyEmailView, CustomRegisterView, CustomLoginView, \
    ResendEmailVerificationView, get_user_info

# urls.py (development only)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('ecommerce/', include('ecommerce.urls')),
                  path('api/', include('api.urls')),
                  path('auth/login/', CustomLoginView.as_view(), name="rest_login"),
                  path('auth/', include('dj_rest_auth.urls')),  # Login, Logout, Password Reset
                  path('auth/registration/account-confirm-email/<str:key>/', CustomVerifyEmailView.as_view(),
                       name="account_confirm_email"),
                  path('auth/register/', CustomRegisterView.as_view(), name="rest_register"),
                  path('auth/resend-email-verification/', ResendEmailVerificationView.as_view(),
                       name="resend-email-verification"),
                  path('auth/registration/', include('dj_rest_auth.registration.urls')),
                  # Registration + Email Verification
                  path('auth/user-info/', get_user_info, name="user-info")

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
