A common best practice when building a modern SPA (single‐page application) with a Django REST backend and a React frontend is to use token‐based authentication with short‐lived access tokens (and refresh tokens) via JSON Web Tokens (JWT). This approach keeps your API stateless, makes scaling easier, and separates authentication concerns from the frontend.

One popular choice for Django is the [**djangorestframework-simplejwt**](https://github.com/jazzband/djangorestframework-simplejwt) package, which handles JWT issuing, refreshing, and verification.

Below is an example setup with Django and React.

---

## Django Setup

### 1. Install Dependencies

Install Django, Django REST framework, and Simple JWT:

```bash
pip install django djangorestframework djangorestframework-simplejwt
```

### 2. Configure Django Settings

In your `settings.py`, add the necessary apps and configure the REST framework to use JWT authentication:

```python
# settings.py

INSTALLED_APPS = [
    # ... your other apps ...
    'rest_framework',
    'rest_framework_simplejwt',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # Optionally, set default permissions if most endpoints require authentication
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# For production, ensure you use HTTPS and set appropriate CORS and CSRF settings.
```

### 3. Set Up URLs for Token Endpoints

Add JWT token obtain and refresh endpoints in your Django `urls.py`:

```python
# urls.py

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from myapp.views import HelloWorld  # Example protected view

urlpatterns = [
    # JWT endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Example protected API endpoint
    path('api/hello/', HelloWorld.as_view(), name='hello_world'),
]
```

### 4. Create a Protected API View

Here’s a simple view that returns a message if the user is authenticated:

```python
# views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class HelloWorld(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        content = {'message': f'Hello, {request.user.username}!'}
        return Response(content)
```

---

## React Frontend Setup

In your React app, you can handle login and then include the JWT in the Authorization header when making API requests. (Note: For security, consider storing tokens in httpOnly cookies instead of localStorage in a production app to mitigate XSS risks.)

### 1. Example Login Component

```jsx
// Login.js

import React, { useState } from 'react';

function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const login = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/token/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      if (!response.ok) {
        throw new Error('Login failed');
      }
      const data = await response.json();
      // Save the tokens (access and refresh). In production, consider a more secure storage.
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      onLogin();
    } catch (error) {
      console.error('Error during login:', error);
    }
  };

  return (
    <div>
      <h2>Login</h2>
      <input 
        type="text" 
        placeholder="Username" 
        value={username}
        onChange={e => setUsername(e.target.value)}
      />
      <br />
      <input 
        type="password" 
        placeholder="Password" 
        value={password}
        onChange={e => setPassword(e.target.value)}
      />
      <br />
      <button onClick={login}>Login</button>
    </div>
  );
}

export default Login;
```

### 2. Fetching Protected Data

When making API requests to protected endpoints, include the JWT in the Authorization header:

```jsx
// FetchData.js

import React, { useEffect, useState } from 'react';

function FetchData() {
  const [message, setMessage] = useState('');

  const fetchData = async () => {
    const token = localStorage.getItem('access_token');
    try {
      const response = await fetch('http://localhost:8000/api/hello/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (!response.ok) {
        throw new Error('Failed to fetch protected data');
      }
      const data = await response.json();
      setMessage(data.message);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return <div>{message ? message : 'Loading...'}</div>;
}

export default FetchData;
```

### 3. Putting It All Together

You might have an `App.js` that conditionally renders the login or the protected content:

```jsx
// App.js

import React, { useState } from 'react';
import Login from './Login';
import FetchData from './FetchData';

function App() {
  const [loggedIn, setLoggedIn] = useState(
    !!localStorage.getItem('access_token')
  );

  return (
    <div className="App">
      {loggedIn ? (
        <>
          <h1>Protected Content</h1>
          <FetchData />
        </>
      ) : (
        <Login onLogin={() => setLoggedIn(true)} />
      )}
    </div>
  );
}

export default App;
```

---

## Additional Considerations

- **Security:**  
  - **Token Storage:** Although the example uses `localStorage` for simplicity, storing tokens in memory or using HttpOnly cookies is more secure because it helps mitigate XSS vulnerabilities.
  - **HTTPS:** Always serve your application over HTTPS in production.
  - **CORS & CSRF:** Configure CORS (Cross-Origin Resource Sharing) properly if your React and Django apps are hosted on different domains. If you switch to cookie-based authentication, implement proper CSRF protection.

- **Token Refreshing:**  
  Use the refresh token endpoint to obtain a new access token when the current one expires. This logic can be added to your React code (or managed by an HTTP client library like Axios with interceptors).

By following this approach, you maintain a clear separation between your authentication mechanism and your application logic while adhering to modern best practices.