# What is the relationship between dj-rest-auth and dj-allauth

### Relationship Between `allauth` and `dj-rest-auth`
`dj-rest-auth` is a Django package that provides RESTful authentication APIs for Django applications, particularly useful when building APIs with Django REST Framework (DRF). It works alongside `django-allauth`, which is a comprehensive authentication and registration framework for Django.

Here’s how they relate:

1. **`dj-rest-auth` as an API Wrapper**  
   - `dj-rest-auth` provides REST API endpoints for authentication (login, logout, password reset, etc.).
   - It is designed to work with Django’s built-in authentication system.
   - By default, it integrates with `django-allauth` for features like registration and email verification.

2. **`django-allauth` for Extended Authentication**  
   - `django-allauth` provides a robust system for authentication, including social authentication (Google, Facebook, etc.), email verification, and user registration.
   - `dj-rest-auth.registration` depends on `django-allauth` to handle user registration, email confirmation, and social authentication workflows.

### How Your Code Uses Them:
```python
path('auth/', include('dj_rest_auth.urls')),  # Login, Logout, Password Reset
path('auth/registration/', include('dj_rest_auth.registration.urls')),  # Registration + Email Verification
```
- `dj_rest_auth.urls` provides endpoints like:
  - `auth/login/` → Login with username/password
  - `auth/logout/` → Logout the user
  - `auth/password/reset/` → Reset password flow

- `dj_rest_auth.registration.urls` (which requires `django-allauth`) provides:
  - `auth/registration/` → User registration
  - `auth/registration/verify-email/` → Email verification after sign-up
  - `auth/registration/resend-email/` → Resend email verification

### Dependencies:
- `dj-rest-auth` can work independently but provides extended functionality when combined with `django-allauth`.
- If you need social authentication (e.g., login via Google/Facebook), you must install and configure `django-allauth`.

### Summary:
- `dj-rest-auth` → Provides REST API authentication endpoints.
- `django-allauth` → Handles user registration, email verification, and social authentication.
- `dj-rest-auth.registration` → Uses `django-allauth` for user registration and email verification.

Would you like help configuring them in your project? 🚀