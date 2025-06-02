# What is SSLCertVerificationError

The error you’re encountering is due to your Django app failing to send a confirmation email 
because of an SSL certificate verification issue when establishing 
a secure connection to your SMTP server:

```bash
ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1010)
```

This means Python’s ssl library cannot verify the SSL certificate of the SMTP server 
(like Gmail, SendGrid, etc.) because your system is missing or not properly linked 
to the root certificates needed for verification.

⸻

✅ Solution

## Step 1: Install or Update Certificates (macOS specific)

Since you’re using macOS, Python 3.12 installed from python.org might not have access 
to system root certificates by default.

Run this script that comes with Python installation:

```bash
/Applications/Python\ 3.12/Install\ Certificates.command
```

This installs the required certificates Python needs for SSL verification.

⸻

## Step 2: Restart Your App

After installing the certificates, restart your Django development server:

```bash
python manage.py runserver
```

Then try registering a user again.

⸻

✅ Optional: Bypass Certificate Verification (Not Recommended for Production)

If you are just testing locally and want to temporarily bypass SSL verification (again, not safe for production):

Edit your Django settings:
```python
import ssl
import smtplib

ssl._create_default_https_context = ssl._create_unverified_context
```

Or override Django’s email backend to use a custom SMTP connection that skips verification.

But again: Do not use this in production — this undermines SSL security.

⸻

## ✅ Step 3: Double-check Django email settings

Make sure you have correct values in your settings.py:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Or your SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@example.com'
EMAIL_HOST_PASSWORD = 'your_app_password'  # Use App Password if using Gmail
```

⸻

If the error persists even after running Install Certificates.command, 
let me know and we’ll try a deeper fix.