To implement **"Forgot Password"** functionality using Django with `dj-rest-auth` and `allauth`, you already have most of it configured if you're using:

```python
path("auth/", include("dj_rest_auth.urls")),  # includes password reset URLs
```

Here's a full step-by-step explanation and customization options:

---

## ✅ 1. **Built-in URL for Password Reset**

The line:

```python
path("auth/", include("dj_rest_auth.urls"))
```

includes endpoints like:

* `auth/password/reset/` – send reset email
* `auth/password/reset/confirm/` – confirm password reset (set new password)

---

## ✅ 2. **Required Settings (for email sending)**

In your `settings.py`, make sure the following are configured correctly:

```python
# Email backend for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'your.smtp.server.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your@email.com'
EMAIL_HOST_PASSWORD = 'yourpassword'
DEFAULT_FROM_EMAIL = 'Your App <your@email.com>'
```

During development, you can use the console backend:

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

---

## ✅ 3. **Frontend Integration Example (API Flow)**

You typically POST to:

* `POST /auth/password/reset/`
  Body:

  ```json
  {
    "email": "user@example.com"
  }
  ```

  ✅ This triggers an email with a link like:

  ```
  http://your-frontend-site.com/reset-password-confirm/<uidb64>/<token>/
  ```

* Then `POST` to `/auth/password/reset/confirm/` with:

  ```json
  {
    "uid": "<uidb64>",
    "token": "<token>",
    "new_password1": "newsecurepassword",
    "new_password2": "newsecurepassword"
  }
  ```

---

## ✅ 4. **Optional Customization**

If you want to **customize the reset email**, override the templates:

Create:

* `templates/account/email/password_reset_key_message.txt`
* `templates/account/email/password_reset_key_subject.txt`

Example for `password_reset_key_message.txt`:

```jinja2
You're receiving this email because you requested a password reset.

Please go to the following page and choose a new password:

{{ protocol }}://{{ domain }}/reset-password-confirm/{{ uid }}/{{ token }}/

Your username, in case you've forgotten: {{ user.get_username }}

Thanks for using our site!
```

And for `password_reset_key_subject.txt`:

```text
Password Reset Requested
```

---

## ✅ 5. **Testing**

Try:

```bash
curl -X POST http://localhost:8000/auth/password/reset/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

---

## Summary

You already included:

```python
path("auth/", include("dj_rest_auth.urls"))
```

So:

* You already have the forgot-password endpoints!
* Just configure your email backend
* Optionally customize templates
* Optionally build your frontend to consume `/auth/password/reset/` and `/auth/password/reset/confirm/`

Let me know if you want to test email sending or customize the password reset link to fit a frontend app like React.


Built React component that posts to `/auth/password/reset` with email and I could receive email with link like below

- http://localhost:8000/auth/password/reset/confirm/5/cqrr9w-da7f6f242a8a70fd4ccf2c64521a938f/

Above link has <uid> and <token> part
I need to build `view` that extracts <uid> and <token> and gets user input to specify new password two times and POST 

# About processing password reset from email link
Thanks for the screenshot and email preview — you're currently hitting Django’s **default HTML-based password reset confirm page**, which isn't what you want in a React app. You're also using the default `dj-rest-auth` behavior, which builds the reset URL pointing to Django’s internal view.

---

### ✅ Your Goal:

You want the reset link to point to your **React app** instead, e.g.:

```
http://localhost:3000/reset-password-confirm/<uid>/<token>/
```

And then your **React component** will handle setting the new password via the API.

---

## 🔧 Fix in 2 Steps

---

### ✅ Step 1: **Tell `dj-rest-auth` to use your frontend reset URL**

In `settings.py`, add this setting:

```python
DJANGO_REST_AUTH = {
    'PASSWORD_RESET_CONFIRM_URL': 'reset-password-confirm/{uid}/{token}/',
    'PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND': True,  # optional
}
```

This replaces the link in the email with:

```
http://localhost:8000/reset-password-confirm/Ng/abc123token/
```

Now let’s rewrite the domain too 👇

---

### ✅ Step 2: **Override the domain in the reset email**

Add this to `settings.py`:

```python
from django.urls import reverse_lazy

# Optional: so emails show http://localhost:3000 instead of backend's domain
SITE_DOMAIN = "localhost:3000"
SITE_NAME = "My React App"

ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"
DEFAULT_FROM_EMAIL = "webmaster@localhost"

# This is used to construct absolute URLs in email
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = "/"
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = "/"
```

If that doesn't take effect, a more direct way is to **override the email sending logic** or set up a custom form with a patched `url_generator`. Let me know if you'd like that.

---

## ✅ Bonus: Your React Route

Now create a React route:

```jsx
<Route path="/reset-password-confirm/:uid/:token" element={<ResetPasswordConfirm />} />
```

And your `ResetPasswordConfirm` component should:

1. Show a form with two fields: new\_password1 + new\_password2
2. On submit, `POST` to:

   ```
   POST /auth/password/reset/confirm/
   ```

   with JSON like:

   ```json
   {
     "uid": "Ng",         // from URL
     "token": "abc123",   // from URL
     "new_password1": "mySecurePassword123",
     "new_password2": "mySecurePassword123"
   }
   ```

Would you like me to give you the full React component (`ResetPasswordConfirm.jsx`) for this?

