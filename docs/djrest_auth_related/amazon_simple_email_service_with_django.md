# How to integrate Amazon SES with Django app

Using **Amazon Simple Email Service (SES)** with your Django application requires setting up **AWS SES**, configuring your **Django email settings**, and ensuring emails are properly sent from your local development environment.

---

## **Step 1: Set Up Amazon SES**
### **1.1 Sign Up for AWS SES**
- Go to the **AWS SES Console**: [Amazon SES](https://aws.amazon.com/ses/)
- If you don't have an AWS account, sign up and verify your identity.

### **1.2 Verify an Email Address (For Sandbox Mode)**
By default, SES starts in **sandbox mode**, meaning you can only send emails to verified addresses.
- In the **SES Console**:
  1. Click **Verified identities**.
  2. Click **Create identity** → Choose **Email address**.
  3. Enter your email and click **Verify**.
  4. Check your email inbox for a verification link and confirm.

> 🚀 **To send emails to unverified addresses**, you need to **request production access** in **SES Sending Limits**.

---

## **Step 2: Get Your AWS SES SMTP Credentials**
Amazon SES provides SMTP credentials to send emails.

1. In **AWS Console**, go to **SES** → **SMTP Settings**.
2. Click **Create My SMTP Credentials**.
3. AWS generates an **SMTP Username** and **Password**.
4. **Save these credentials**; you will need them in Django.

---

## **Step 3: Install Required Libraries**
You'll need `boto3` (AWS SDK for Python) and `django-anymail` (optional for better email handling).

```bash
pip install boto3 django-anymail
```

---

## **Step 4: Configure Django Settings**
Edit your `settings.py` file:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'  # Check your SES region
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-smtp-username'  # From AWS SES SMTP credentials
EMAIL_HOST_PASSWORD = 'your-smtp-password'  # From AWS SES SMTP credentials
DEFAULT_FROM_EMAIL = 'your-verified-email@example.com'  # Must be a verified email in SES
```

If you're using **django-anymail**, you can also configure it like this:

```python
INSTALLED_APPS += ['anymail']

ANYMAIL = {
    "AMAZON_SES_CLIENT_PARAMS": {
        "region_name": "us-east-1",  # Change to your AWS region
    },
}

EMAIL_BACKEND = "anymail.backends.amazon_ses.EmailBackend"
DEFAULT_FROM_EMAIL = "your-verified-email@example.com"
```

---

## **Step 5: Test Sending an Email**
In your Django shell (`python manage.py shell`):

```python
from django.core.mail import send_mail

send_mail(
    "Test Email from Django",
    "This is a test email sent via Amazon SES.",
    "your-verified-email@example.com",
    ["recipient@example.com"],  # This must be a verified email in sandbox mode
    fail_silently=False,
)
```

If everything is configured correctly, you should receive an email! 🎉

---

## **Step 6: Move SES Out of Sandbox Mode (For Production)**
By default, SES is in **sandbox mode**, meaning you can only send emails to verified addresses. To send to any email:
1. Go to **AWS SES Console** → **Sending Limits**.
2. Click **Request Production Access**.
3. Fill out the request form and wait for approval.

---

## **Step 7: Deploy to Production**
Once your Django app is live:
1. Use **environment variables** to store **SMTP credentials** securely.
2. Use **IAM roles and boto3** for better AWS integration.
3. Consider **Amazon SNS** for tracking email delivery status.

---

## **Troubleshooting**
1. **Email not sent?**
   - Check the AWS **SES Sending Metrics** for errors.
   - Ensure your email is **verified** in SES.
   - Check **Django logs** for SMTP errors.

2. **SMTP Authentication error?**
   - Verify **SMTP username and password**.
   - Ensure **SES is in production mode**.

---

🚀 **Now your Django app is sending emails via Amazon SES!** Would you like to extend this by using **AWS SDK (boto3) instead of SMTP**?