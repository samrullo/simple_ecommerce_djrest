# How to override user details that dj_rest_auth Login returns

dj‑rest‑auth returns user details using a serializer that you can override. By default, when you log in (or when you call the user details endpoint), dj‑rest‑auth uses a serializer specified by the setting `REST_AUTH_USER_DETAILS_SERIALIZER` (or a default one if you don’t override it).

To have the login response return your **Customer** model (with its nested **Address** objects) instead of just the basic user fields, you can create a custom user details serializer that includes these related objects. Then, set that serializer in your Django settings.

Below is an example of how to do this:

---

### 1. Create a Custom User Details Serializer

Suppose you have a **Customer** model (possibly with a OneToOneField or ForeignKey to your user) and an **Address** model related to Customer. You might create serializers like this:

```python
# your_app/serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers
from ecommerce.models import Customer, Address

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'street', 'city', 'state', 'zip_code', 'country', 'is_default']

class CustomerSerializer(serializers.ModelSerializer):
    # Assuming Customer has a reverse relationship to Address via address_set.
    addresses = AddressSerializer(source='address_set', many=True, read_only=True)
    
    class Meta:
        model = Customer
        fields = ['id', 'phone', 'addresses']  # Add any additional fields from Customer

class CustomUserSerializer(serializers.ModelSerializer):
    # Assuming you have a OneToOneField from User to Customer named "customer"
    customer = CustomerSerializer(read_only=True)
    
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'customer']
```

> **Note:**  
> - If your **Customer** relationship is set up differently (for example, if a user may have multiple customers or is linked differently), adjust the serializer accordingly.  
> - In the above example, we assume that your **Customer** is accessible as `user.customer` and that **Address** objects are accessible through the reverse relationship `customer.address_set`.

---

### 2. Configure dj‑rest‑auth to Use Your Custom Serializer

In your `settings.py`, add or update the following setting to point to your custom user details serializer:

```python
REST_AUTH_USER_DETAILS_SERIALIZER = 'your_app.serializers.CustomUserSerializer'
```

Replace `your_app.serializers.CustomUserSerializer` with the actual Python import path for your serializer.

---

### 3. Test the Login Endpoint

Now, when you log in using your API endpoint (for example, via curl):

```bash
curl -X POST http://localhost:8000/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"email": "naira@mail.com", "password": "kichk!nasir"}'
```

The JSON response should include an expanded `user` field that looks something like this:

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9....",
  "refresh": "",
  "user": {
      "id": 39,
      "username": "naira",
      "email": "naira@mail.com",
      "first_name": "Naira",
      "last_name": "Amrulloeva",
      "customer": {
          "id": 7,
          "phone": "1234567890",
          "addresses": [
              {
                  "id": 1,
                  "street": "Ushirohirai 170 ban 315 goshitu",
                  "city": "Nagareyama",
                  "state": "Chiba",
                  "zip_code": "270-0151",
                  "country": "Japan",
                  "is_default": true
              }
              // ... other addresses if any ...
          ]
      }
  }
}
```

This way, your login response returns the **Customer** model along with all related **Address** instances.

---

### Summary

1. **Create a custom serializer** (`CustomUserSerializer`) that nests your **Customer** and **Address** serializers.
2. **Set the `REST_AUTH_USER_DETAILS_SERIALIZER` setting** in your Django settings to point to your custom serializer.
3. **Test the endpoint** to verify the response includes the nested related objects.

By following these steps, you can override the default user details response so that it returns the full customer profile with its addresses after login.