# Fastest way for email verification

For the **fastest** and **cheapest** way to implement email verification for user registration in your **Django REST backend** and **React frontend**, follow these steps:

---

## 1️⃣ **Use Django's Built-in User Model & DRF Authentication**
Django comes with built-in **email confirmation** and **account activation** capabilities.

- We will use **Django’s default User model**.
- We will generate an **email confirmation link** containing a **token**.
- Users will receive a **verification email**.
- Clicking the link will **activate** their account.

---

## 2️⃣ **Install Required Packages**
```bash
pip install django-allauth djangorestframework-simplejwt dj-rest-auth
```
- `django-allauth` → Manages user authentication.
- `dj-rest-auth` → Provides login, logout, registration APIs.
- `djangorestframework-simplejwt` → Handles token authentication.

---

## 3️⃣ **Configure Django Settings**
In `settings.py`, add:
```python
INSTALLED_APPS = [
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rest_framework',
    'dj_rest_auth',
    'dj_rest_auth.registration',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Email Backend (Use Console for Testing)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Change this later for production

SITE_ID = 1

# Allauth Configuration
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'  # Require email confirmation
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False  # Optional, can register with email only

REST_USE_JWT = True
```

---
## 4️⃣ **Set Up User Registration & Email Confirmation APIs**
In `urls.py`, add:

```python
from django.urls import path, include

urlpatterns = [
    path('auth/', include('dj_rest_auth.urls')),  # Login, Logout, Password Reset
    path('auth/registration/', include('dj_rest_auth.registration.urls')),  # Registration + Email Verification
]
```

This will automatically create:
1. **User Registration API** → `POST /auth/registration/`
2. **Email Confirmation API** → `POST /auth/registration/verify-email/`
3. **Login API** → `POST /auth/login/`
4. **Logout API** → `POST /auth/logout/`

---

## 5️⃣ **Testing Email Verification Locally**
Since we set `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'`, Django will print emails in the console.

### **Steps to Test**
1. **Register a new user**
   ```json
   POST http://127.0.0.1:8000/auth/registration/
   {
     "email": "user@example.com",
     "password1": "StrongPassword123!",
     "password2": "StrongPassword123!"
   }
   ```

2. **Check the console output**
   Django will print something like this:
   ```
   Subject: Account confirmation
   Please click the following link to confirm your email:
   http://127.0.0.1:8000/auth/registration/verify-email/?key=generated_token
   ```

3. **Simulate clicking the confirmation link**
   Send a `POST` request to confirm:
   ```json
   POST http://127.0.0.1:8000/auth/registration/verify-email/
   {
     "key": "generated_token_from_email"
   }
   ```

4. **User is now activated** and can log in.

---

## 6️⃣ **Send Real Emails (For Production)**
For a **cheap and fast** email service, use **Gmail SMTP** or **Brevo (formerly Sendinblue)**.

### **Gmail SMTP**
Add to `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_gmail@gmail.com'
EMAIL_HOST_PASSWORD = 'your_gmail_app_password'  # Use an App Password
```
- Generate an **App Password** from Google if using Gmail.

---

## 7️⃣ **React Frontend - Handle Registration & Confirmation**
In **React**, use `axios` to call the APIs.

### **Register User**
```javascript
import axios from "axios";

const registerUser = async (email, password1, password2) => {
  try {
    const response = await axios.post("http://127.0.0.1:8000/auth/registration/", {
      email,
      password1,
      password2,
    });
    alert("Check your email for confirmation!");
  } catch (error) {
    console.error("Registration error:", error);
  }
};
```

### **Confirm Email**
```javascript
const confirmEmail = async (token) => {
  try {
    await axios.post("http://127.0.0.1:8000/auth/registration/verify-email/", {
      key: token,
    });
    alert("Email confirmed! You can now log in.");
  } catch (error) {
    console.error("Email confirmation error:", error);
  }
};
```

---

## 🎯 **Final Summary**
1. **Use `dj-rest-auth` with `django-allauth`** for fast user registration.
2. **Email verification is automatic** via `/auth/registration/verify-email/`.
3. **For testing**, use `EMAIL_BACKEND = console`.
4. **For real emails**, configure SMTP (Gmail/Brevo).
5. **React frontend** makes API calls to register and verify users.

This is the **fastest** and **cheapest** way to set up user registration with email confirmation in Django REST and React. 🚀 Let me know if you need more details!


# Registering user with additional fields

Got it! Since you want to **register a user with additional information** such as **full name, phone, and addresses**, I'll show you how to extend **Django’s user registration** while keeping the email confirmation flow.

---

# ✅ **Updated Plan**
1. **Modify the `User` model to store additional info (`Customer` model)**.
2. **Customize the registration serializer** to handle `full_name`, `phone`, and `addresses`.
3. **Ensure the email confirmation flow remains intact**.
4. **Allow users to activate accounts after verifying their email**.

---

## 1️⃣ **Modify the Models**
Since `auth.User` already exists, we will store additional details in the `Customer` model.

### **models.py**
```python
from django.contrib.auth.models import User
from django.db import models

class Customer(models.Model):
    """
    Stores customer details linked to the User model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer")
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField()

    def __str__(self):
        return self.user.username


class Address(models.Model):
    """
    Stores multiple addresses for a customer.
    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="addresses")
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.customer.user.username} - {self.street}"
```

---

## 2️⃣ **Customize the Registration Serializer**
We need to **extend the default user registration serializer** to accept `full_name`, `phone`, and `addresses`.

### **serializers.py**
```python
from django.contrib.auth.models import User
from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from .models import Customer, Address

class AddressSerializer(serializers.ModelSerializer):
    """
    Serialize Address details.
    """
    class Meta:
        model = Address
        fields = ['street', 'city', 'state', 'zip_code', 'country', 'is_default']


class CustomRegisterSerializer(RegisterSerializer):
    """
    Extends the default registration serializer to include full_name, phone, and addresses.
    """
    full_name = serializers.CharField(required=True, max_length=200)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=20)
    addresses = AddressSerializer(many=True, required=False)

    def get_cleaned_data(self):
        """
        Include additional fields in the user creation process.
        """
        data = super().get_cleaned_data()
        data['full_name'] = self.validated_data.get('full_name', '')
        data['phone'] = self.validated_data.get('phone', '')
        data['addresses'] = self.validated_data.get('addresses', [])
        return data

    def save(self, request):
        """
        Save the user and create associated Customer and Address entries.
        """
        user = super().save(request)  # Create User
        full_name = self.validated_data.get('full_name')
        phone = self.validated_data.get('phone')
        addresses_data = self.validated_data.get('addresses', [])

        # Create Customer profile
        customer = Customer.objects.create(user=user, full_name=full_name, phone=phone, email=user.email)

        # Create associated addresses
        for address_data in addresses_data:
            Address.objects.create(customer=customer, **address_data)

        return user
```
🔹 **What This Does:**
- Extends `RegisterSerializer` to accept `full_name`, `phone`, and `addresses`.
- Saves additional user details in `Customer` and `Address` models.

---

## 3️⃣ **Configure Custom Registration Serializer**
Tell `dj-rest-auth` to use our custom serializer.

### **settings.py**
```python
INSTALLED_APPS = [
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rest_framework',
    'dj_rest_auth',
    'dj_rest_auth.registration',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

REST_AUTH_REGISTER_SERIALIZERS = {
    "REGISTER_SERIALIZER": "your_app.serializers.CustomRegisterSerializer",
}

# Email verification settings
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_USERNAME_REQUIRED = False

# Email Backend for Testing
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
SITE_ID = 1
```

---

## 4️⃣ **Modify URLs to Support Registration**
In **urls.py**, update the endpoints.

```python
from django.urls import path, include

urlpatterns = [
    path('auth/', include('dj_rest_auth.urls')),  # Login, Logout, Password Reset
    path('auth/registration/', include('dj_rest_auth.registration.urls')),  # Registration + Email Verification
]
```

Now, our API **automatically** handles:
1. **Registering users with full_name, phone, and addresses**
2. **Sending an email verification link**
3. **Activating users upon email confirmation**

---

## 5️⃣ **Test User Registration**
### **Register User**
Make a `POST` request to:
```
POST http://127.0.0.1:8000/auth/registration/
```
#### **Request Body (JSON)**
```json
{
  "email": "user@example.com",
  "password1": "StrongPassword123!",
  "password2": "StrongPassword123!",
  "full_name": "John Doe",
  "phone": "+1234567890",
  "addresses": [
    {
      "street": "123 Main St",
      "city": "New York",
      "state": "NY",
      "zip_code": "10001",
      "country": "USA",
      "is_default": true
    }
  ]
}
```
#### **Expected Response**
```json
{
  "detail": "Verification email sent."
}
```

---

## 6️⃣ **Confirm Email (Simulating the User Clicking the Link)**
- Check your console (`EMAIL_BACKEND = console`).
- You will see an email containing a **verification link**.
- Copy the **key** from the email and send a **POST request**:

```
POST http://127.0.0.1:8000/auth/registration/verify-email/
```

#### **Request Body**
```json
{
  "key": "paste_the_token_here"
}
```

#### **Expected Response**
```json
{
  "detail": "Account successfully verified."
}
```
Now, the user can log in.

---

## 7️⃣ **React Frontend**
### **Register User in React**
```javascript
import axios from "axios";

const registerUser = async (email, password1, password2, fullName, phone, addresses) => {
  try {
    const response = await axios.post("http://127.0.0.1:8000/auth/registration/", {
      email,
      password1,
      password2,
      full_name: fullName,
      phone,
      addresses,
    });
    alert("Check your email for confirmation!");
  } catch (error) {
    console.error("Registration error:", error);
  }
};
```

### **Confirm Email**
```javascript
const confirmEmail = async (token) => {
  try {
    await axios.post("http://127.0.0.1:8000/auth/registration/verify-email/", {
      key: token,
    });
    alert("Email confirmed! You can now log in.");
  } catch (error) {
    console.error("Email confirmation error:", error);
  }
};
```

---

## ✅ **Final Summary**
1. **Extended User Registration** to include `full_name`, `phone`, and `addresses`.
2. **Used `dj-rest-auth` + `django-allauth`** for email verification.
3. **Users receive a confirmation email** before activation.
4. **React frontend integrates easily** via API calls.

🚀 **This is the FASTEST and CHEAPEST way** to implement user registration with email verification! Let me know if you need help!


# Email verification template

This error occurs because the email confirmation view (which inherits from Django’s `TemplateView` via `TemplateResponseMixin`) is expecting a `template_name` or a custom implementation of `get_template_names()`. In other words, dj_rest_auth’s default email confirmation view is trying to render an HTML template, but none is defined.

There are two main approaches to resolve this issue:

---

## Option 1. Provide a Template

If you plan to show a confirmation page after a user clicks the email link, you need to supply a template.

1. **Create the Template**

   Create a file such as:

   ```
   templates/account/email/email_confirm.html
   ```

   For example, the file might contain:

   ```html
   <!DOCTYPE html>
   <html lang="en">
   <head>
       <meta charset="UTF-8" />
       <meta name="viewport" content="width=device-width, initial-scale=1.0" />
       <title>Email Confirmed</title>
   </head>
   <body>
       <h1>Email Confirmed</h1>
       <p>Your email has been successfully verified.</p>
   </body>
   </html>
   ```

2. **Override or Configure the View**

   If you’re using dj_rest_auth’s default URL patterns, you might need to override the email confirmation view to specify the template. For example, create a custom view:

   ```python
   # views.py
   from dj_rest_auth.registration.views import VerifyEmailView

   class CustomVerifyEmailView(VerifyEmailView):
       template_name = "account/email/email_confirm.html"
   ```

3. **Update Your URL Patterns**

   In your `urls.py`, replace the default confirmation view with your custom view:

   ```python
   # urls.py
   from django.urls import path
   from .views import CustomVerifyEmailView

   urlpatterns = [
       # ... your other URL patterns ...
       path(
           "auth/registration/account-confirm-email/<str:key>/",
           CustomVerifyEmailView.as_view(),
           name="account_confirm_email"
       ),
   ]
   ```

   Now, when a user clicks the confirmation link, Django will render the provided template.

---

## Option 2. Return a JSON Response Instead of Rendering a Template

If you’re building a pure API (for example, if your frontend handles redirection and display), you might prefer to return a JSON response rather than rendering an HTML page.

1. **Create a Custom View**

   You can subclass the `VerifyEmailView` and override the `get` method to return a JSON response:

   ```python
   # views.py
   from dj_rest_auth.registration.views import VerifyEmailView
   from rest_framework.response import Response
   from rest_framework import status

   class CustomVerifyEmailView(VerifyEmailView):
       def get(self, *args, **kwargs):
           self.object = self.get_object()  # Fetch the email confirmation object
           self.object.confirm()  # Confirm the email
           return Response({"detail": "Email confirmed"}, status=status.HTTP_200_OK)
   ```

2. **Update Your URL Patterns**

   As in Option 1, point your confirmation URL to your custom view:

   ```python
   # urls.py
   from django.urls import path
   from .views import CustomVerifyEmailView

   urlpatterns = [
       # ... your other URL patterns ...
       path(
           "auth/registration/account-confirm-email/<str:key>/",
           CustomVerifyEmailView.as_view(),
           name="account_confirm_email"
       ),
   ]
   ```

With this change, the confirmation endpoint will return a JSON response instead of attempting to render an HTML template.

---

## Summary

- **Error Cause:**  
  The default confirmation view from dj_rest_auth (or django-allauth) expects a template to be rendered but no `template_name` is defined.

- **Solution Options:**  
  1. **Provide a template:** Create an HTML template and override the view to use that template.
  2. **Return JSON:** Override the view to return a JSON response if your frontend will handle the confirmation UI.

Choose the option that best fits your project’s architecture and how you want to handle email confirmations.

Below is example email verification url generated by dj_rest_auth.registration : 
 http://localhost:8000/auth/registration/account-confirm-email/Mg:1theL5:657yuELN2_5HRquGBPcptRTcgtltGyxB21YSCwnY4y8/

# Register user with extra fields

To include additional fields (like first name, last name, address, and phone number) when registering a user with dj‑rest‑auth, you'll need to customize the registration serializer (and possibly the allauth adapter) so that those fields are accepted, validated, and saved.

Below are the steps and sample code to achieve this:

---

## 1. Extend the Registration Serializer

dj‑rest‑auth uses a default registration serializer (which, in turn, often leverages django‑allauth). You can extend it to add your custom fields.

**Create a custom serializer, e.g., in `your_app/serializers.py`:**

```python
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers

class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True, max_length=30)
    last_name = serializers.CharField(required=True, max_length=30)
    address = serializers.CharField(required=True, max_length=255)
    phone_number = serializers.CharField(required=True, max_length=20)

    def get_cleaned_data(self):
        """
        Gather all validated fields including the extra ones.
        """
        data = super().get_cleaned_data()
        data['first_name'] = self.validated_data.get('first_name', '')
        data['last_name'] = self.validated_data.get('last_name', '')
        data['address'] = self.validated_data.get('address', '')
        data['phone_number'] = self.validated_data.get('phone_number', '')
        return data
```

This serializer extends the default one and adds the fields you want to capture. The `get_cleaned_data()` method is used by dj‑rest‑auth to pass the data to the user creation process.

---

## 2. Configure dj‑rest‑auth to Use Your Serializer

In your Django settings (typically in `settings.py`), tell dj‑rest‑auth to use your custom registration serializer:

```python
REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'your_app.serializers.CustomRegisterSerializer',
}
```

Make sure to replace `"your_app.serializers.CustomRegisterSerializer"` with the correct Python path to your serializer.

---

## 3. (Optional) Update the Allauth Adapter

If you need to perform additional processing (for example, saving the extra fields on the user model), you might also need to override the allauth adapter. This step is especially important if your User model already contains these extra fields.

**Create a custom adapter, e.g., in `your_app/adapters.py`:**

```python
from allauth.account.adapter import DefaultAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        """
        Save extra fields on the user instance.
        """
        user = super().save_user(request, user, form, commit=False)
        data = form.cleaned_data
        user.first_name = data.get('first_name', '')
        user.last_name = data.get('last_name', '')
        # If your user model has these fields:
        user.address = data.get('address', '')
        user.phone_number = data.get('phone_number', '')
        if commit:
            user.save()
        return user
```

Then configure allauth to use your custom adapter by adding the following to your settings:

```python
ACCOUNT_ADAPTER = 'your_app.adapters.CustomAccountAdapter'
```

Again, ensure that the path matches your project structure.

---

## 4. Make Sure Your User Model Can Store the Extra Fields

If you’re using Django’s default User model, note that it doesn’t include fields like `address` or `phone_number` by default. You have a few options:

- **Extend the User Model:**  
  Create a custom user model that adds these fields.

- **Create a Profile Model:**  
  Create a separate model (often called `UserProfile`) that has a one‑to‑one relationship with the User model, and save the extra fields there.

Make sure that your custom serializer and adapter reflect how you’ve set up your user data.

---

## 5. Testing Your Endpoint

Now you can register a user using your custom fields with a command like:

```bash
curl -X POST http://localhost:8000/auth/registration/ \
  -H "Content-Type: application/json" \
  -d '{
        "email": "dinara@mail.com",
        "password1": "thepassword",
        "password2": "thepassword",
        "first_name": "Dinara",
        "last_name": "Smith",
        "address": "123 Main St",
        "phone_number": "1234567890"
      }'
```

The serializer will validate and clean the data, and the adapter (if used) will ensure the extra fields are saved on your user model.

---

## Summary

- **Customize the Registration Serializer:**  
  Extend `RegisterSerializer` to include the extra fields and update `get_cleaned_data()`.

- **Configure dj‑rest‑auth Settings:**  
  Point `REST_AUTH_REGISTER_SERIALIZERS` to your custom serializer.

- **(Optional) Override the Allauth Adapter:**  
  If needed, override `save_user` to handle the new fields.

- **Ensure Your Data Model Supports Extra Fields:**  
  Either extend your User model or create an associated profile model.

By following these steps, you'll be able to register users with additional fields using dj‑rest‑auth.


# How does RegisterSerializer know about Account Adapter
When using dj‑rest‑auth (which builds on django‑allauth), the custom registration serializer’s job is primarily to:

1. **Collect and Validate Input Data:**  
   It defines the extra fields you want to accept (e.g. `first_name`, `last_name`, `phone_number`, and `address`).

2. **Return a Cleaned Data Dictionary:**  
   The serializer’s `get_cleaned_data()` method gathers all the validated fields into a dictionary.

However, the serializer itself doesn’t automatically “know” about related models (like your separate **Customer** model). Instead, the cleaned data is passed along to the account adapter (or another part of the registration process), which is responsible for saving the user—and if needed, creating or updating any related objects.

### How It Works in Practice

1. **Custom Registration Serializer:**  
   You extend the default registration serializer to include your extra fields. For example:

   ```python
   # your_app/serializers.py
   from dj_rest_auth.registration.serializers import RegisterSerializer
   from rest_framework import serializers

   class CustomRegisterSerializer(RegisterSerializer):
       first_name = serializers.CharField(required=True, max_length=30)
       last_name = serializers.CharField(required=True, max_length=30)
       phone_number = serializers.CharField(required=True, max_length=20)
       address = serializers.CharField(required=True, max_length=255)

       def get_cleaned_data(self):
           data = super().get_cleaned_data()
           data['first_name'] = self.validated_data.get('first_name', '')
           data['last_name'] = self.validated_data.get('last_name', '')
           data['phone_number'] = self.validated_data.get('phone_number', '')
           data['address'] = self.validated_data.get('address', '')
           return data
   ```

   This serializer validates and “cleans” the input data, returning a dictionary that now includes keys for `first_name`, `last_name`, `phone_number`, and `address`.

2. **Custom Account Adapter:**  
   The next step is to ensure that the extra data is used to update both the **User** model (for fields like `first_name` and `last_name`) and the related **Customer** model (for `phone_number` and `address`). To do that, override the adapter’s `save_user()` method:

   ```python
   # your_app/adapters.py
   from allauth.account.adapter import DefaultAccountAdapter
   from your_app.models import Customer  # Import your Customer model

   class CustomAccountAdapter(DefaultAccountAdapter):
       def save_user(self, request, user, form, commit=True):
           """
           Save the user with extra fields and create/update the related Customer.
           """
           # Save basic user information first
           user = super().save_user(request, user, form, commit=False)
           data = form.cleaned_data
           user.first_name = data.get('first_name', '')
           user.last_name = data.get('last_name', '')
           if commit:
               user.save()
           
           # Now handle the Customer model (which holds phone and address)
           # You can create a new Customer or update an existing one as needed.
           Customer.objects.create(
               user=user,
               phone=data.get('phone_number', ''),
               address=data.get('address', '')
           )
           return user
   ```

   Here’s what’s happening:
   
   - **User Fields:**  
     The adapter updates the `first_name` and `last_name` on the user instance.

   - **Related Model:**  
     It then creates a **Customer** object (which has a one‑to‑one relationship with the user) using the extra data from the serializer.
   
3. **Configuration:**  
   Finally, let dj‑rest‑auth and allauth know about your custom serializer and adapter by updating your settings:

   ```python
   # settings.py

   REST_AUTH_REGISTER_SERIALIZERS = {
       'REGISTER_SERIALIZER': 'your_app.serializers.CustomRegisterSerializer',
   }

   ACCOUNT_ADAPTER = 'your_app.adapters.CustomAccountAdapter'
   ```

### In Summary

- **The Custom Register Serializer** simply collects and validates the extra fields.  
- **It doesn’t inherently know** about related models such as your **Customer** model.  
- **The Adapter’s Role:**  
  The adapter’s `save_user()` method receives the cleaned data (which includes all the extra fields) and is where you implement the logic to update the **User** model as well as create or update any related models (like **Customer**).

This separation keeps concerns clear: the serializer deals with data validation and cleaning, while the adapter handles the persistence and creation of related objects.