# Get user info with access token

You can use your **`CustomUserSerializer`** in your Django API endpoint to return user info when a valid JWT token is provided. Below are the steps to implement this properly.

---

## **1. Use `CustomUserSerializer` in the API View**
Modify your `views.py` to return user info using your `CustomUserSerializer`:

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import CustomUserSerializer

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    user = request.user
    serializer = CustomUserSerializer(user)  # Serialize user with CustomUserSerializer
    return Response(serializer.data)
```

---

## **2. Add the URL to `urls.py`**
```python
from django.urls import path
from .views import get_user_info

urlpatterns = [
    path("user-info/", get_user_info, name="user-info"),
]
```

---

## **3. Send API Request From Frontend**
You can now call the `/user-info/` endpoint from your frontend **by sending the JWT token**.

### **Using Fetch**
```javascript
fetch("http://127.0.0.1:8000/user-info/", {
  method: "GET",
  headers: {
    "Authorization": `Bearer ${yourAccessToken}`, // Replace with your JWT token
    "Content-Type": "application/json"
  }
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error("Error:", error));
```

### **Using Axios**
```javascript
import axios from "axios";

axios.get("http://127.0.0.1:8000/user-info/", {
  headers: { Authorization: `Bearer ${yourAccessToken}` }
})
.then(response => console.log(response.data))
.catch(error => console.error("Error:", error));
```

---

## **4. Expected API Response**
If the user has an associated `Customer` object, the response will look like:

```json
{
    "id": 51,
    "username": "subkhon",
    "email": "amrulloev.subhon@gmail.com",
    "first_name": "Subkhon",
    "last_name": "Amrulloev",
    "customer": {
        "id": 26,
        "phone": "+998123456789",
        "addresses": [
            {
                "id": 18,
                "street": "Yunusabad",
                "city": "Tashkent",
                "state": "Tashkent",
                "zip_code": "123-4567",
                "country": "Uzbekistan",
                "is_default": true
            }
        ]
    }
}
```

---

## **5. Handling Users Without a `Customer`**
If a user **does not have a `customer` object**, your serializer should return `None` instead of causing an error.

You have already handled this well in your `get_customer` method:

```python
def get_customer(self, obj):
    try:
        customer_obj = obj.customer  # should work if a Customer exists
        return CustomerSerializer(customer_obj).data
    except Exception as e:
        return None  # Ensures no error occurs
```

If the user has **no customer data**, the API will return:

```json
{
    "id": 51,
    "username": "subkhon",
    "email": "amrulloev.subhon@gmail.com",
    "first_name": "Subkhon",
    "last_name": "Amrulloev",
    "customer": null
}
```

---

### ✅ **Final Summary**
✔ **We used `CustomUserSerializer` in an API view.**  
✔ **We ensured that `customer` is safely handled in the serializer.**  
✔ **We made an API call with JWT authentication to get user info.**  
✔ **Frontend can now use this endpoint to display user details.**  

🚀 **Now your Django REST API properly returns user info with JWT authentication!** Let me know if you need any improvements. 😊


Example ```curl``` to get user info with access token

```bash
curl -X GET http://localhost:8000/auth/user-info/ -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM5NjA5MjY0LCJpYXQiOjE3Mzk2MDg5NjQsImp0aSI6ImRiN2FjNDg4YjJmMDRlYTNhMWRiMWMzOTRkMjIwZWQ4IiwidXNlcl9pZCI6NTF9.nEXj19y0WQLZbefLgfxn4jdOS5zZUP5OzIwV_xhfwP0"
```