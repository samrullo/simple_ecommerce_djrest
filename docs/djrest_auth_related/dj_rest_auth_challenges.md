# Getting error no such table account_emailaddresses

Had to run migrations for ```account``` and migrate

```bash
python manage.py makemigrations account
python manage.py migrate account
```

# Getting error no such table authtoken_token
$ python manage.py migrate
Operations to perform:
  Apply all migrations: account, admin, auth, authtoken, contenttypes, ecommerce, sessions, socialaccount
Running migrations:
  Applying authtoken.0001_initial... OK
  Applying authtoken.0002_auto_20160226_1747... OK
  Applying authtoken.0003_tokenproxy... OK
  Applying socialaccount.0001_initial... OK
  Applying socialaccount.0002_token_max_lengths... OK
  Applying socialaccount.0003_extra_data_default_dict... OK


# Account middleware had to be added

I had to add below middleware for makemigrations to work

```python
MIDDLEWARE=[...,
            'allauth.account.middleware.AccountMiddleware',
            ]

```

# Curl for login
Run below

```bash
curl -X POST http://localhost:8000/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"email": "samrullo@mail.com", "password": "your_password"}'
```

# I got dj-rest-auth use JWTSerializer

it turned out REST_AUTH variables takes care of it.
It will store refresh_token in cookie, so from react front you will need to include csrf token

# How do I use refresh token?
When you configure dj‑rest‑auth to store the refresh token in an HTTP‑only cookie, your front end no longer directly accesses the refresh token. Instead, you “use” it by making a request to your token refresh endpoint. Here's how it works:

1. **HTTP‑Only Refresh Token:**  
   - The refresh token is stored in an HTTP‑only cookie, which means it isn’t accessible via JavaScript (for security reasons).  
   - Your browser automatically includes this cookie when you make requests to your server (provided that you include credentials).

2. **Refreshing the Access Token:**  
   - dj‑rest‑auth (often together with SimpleJWT) provides a refresh endpoint (typically something like `/auth/token/refresh/`).  
   - When your access token expires, your front end can send a request to this refresh endpoint.  
   - Because the refresh token is stored in a cookie, the browser will attach it automatically if your request is configured to send credentials (for example, by using `credentials: 'include'` in fetch or `withCredentials: true` in axios).

3. **CSRF Considerations:**  
   - If CSRF protection is enabled, you'll also need to include the CSRF token in your request headers.  
   - The CSRF token is typically provided by Django via another cookie (often named `csrftoken`), which you can read on the client side (if it’s not HTTP‑only) and then include in your request headers as `X-CSRFToken`.

4. **Example Using Fetch:**  
   ```javascript
   fetch('http://localhost:8000/auth/token/refresh/', {
     method: 'POST',
     credentials: 'include', // Ensure cookies are sent
     headers: {
       'Content-Type': 'application/json',
       'X-CSRFToken': csrfToken, // If CSRF protection is enabled
     },
     // You might not need to send any body if the endpoint is set to read the cookie directly.
   })
   .then(response => response.json())
   .then(data => {
     // data should include the new access token (and possibly a new refresh token cookie will be set)
     console.log('New access token:', data.access);
   });
   ```

5. **What You Do on the Front End:**  
   - You don’t manually grab or manage the refresh token. Instead, when you detect that your access token has expired, your front end makes a request to the refresh endpoint.  
   - The server reads the refresh token from the cookie, validates it, and then issues a new access token (and optionally a new refresh token, updating the cookie accordingly).

### In Summary

- **No Direct Access:** Since the refresh token is stored as an HTTP‑only cookie, you don’t have to (and can’t) manually include it in your request body.
- **Automatic Handling:** The browser sends the refresh token automatically with your request (if `credentials: 'include'` is set).
- **Endpoint Responsibility:** Your refresh endpoint handles verifying the refresh token from the cookie and returning new tokens.

This approach improves security by protecting the refresh token from potential XSS attacks while still allowing your application to refresh access tokens seamlessly.

# Don't forget to specify default authentication methods

Specify DEFAULT_AUTHENTICATION_METHOD to have Django properly identify what is authentication method being used.
With below, django will authenticate your API call with access token

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication']
}
```