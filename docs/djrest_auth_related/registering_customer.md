# How to register the user

Since you're building a **Django REST Framework (DRF)** application, you need to create resources for **Customer** and **Address**. Here's a step-by-step guide on how to structure your backend.

---

## 1️⃣ **Serializers (Define API Representation)**
Since `Customer` and `Address` are related, you can create serializers to handle both models.

### `serializers.py`
```python
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Customer, Address

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'street', 'city', 'state', 'zip_code', 'country', 'is_default']

class CustomerSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  # Allow user selection
    addresses = AddressSerializer(many=True, required=False)  # Handle multiple addresses

    class Meta:
        model = Customer
        fields = ['id', 'user', 'name', 'phone', 'email', 'addresses']

    def create(self, validated_data):
        """
        Overriding create to handle nested address creation.
        """
        addresses_data = validated_data.pop('addresses', [])  # Extract addresses
        customer = Customer.objects.create(**validated_data)

        # Create associated addresses
        for address_data in addresses_data:
            Address.objects.create(customer=customer, **address_data)

        return customer
```

---

## 2️⃣ **Views (Define API Logic)**
Now, create views to handle registration and managing customers.

### `views.py`
```python
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Customer, Address
from .serializers import CustomerSerializer, AddressSerializer

class CustomerCreateView(generics.CreateAPIView):
    """
    API to create a Customer with nested addresses.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class CustomerDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single customer's details.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

class AddressCreateView(generics.CreateAPIView):
    """
    API to add an address to a customer.
    """
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
```

---

## 3️⃣ **URLs (Define API Endpoints)**
Add URL routes for customer and address management.

### `urls.py`
```python
from django.urls import path
from .views import CustomerCreateView, CustomerDetailView, AddressCreateView

urlpatterns = [
    path('customers/', CustomerCreateView.as_view(), name='customer-create'),
    path('customers/<int:pk>/', CustomerDetailView.as_view(), name='customer-detail'),
    path('addresses/', AddressCreateView.as_view(), name='address-create'),
]
```

---

## 4️⃣ **Handling User Registration**
Since `Customer` is linked to `User`, you need to ensure that users can register.

### Add User Registration Serializer
```python
class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Register user and create a linked Customer object.
    """
    name = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(write_only=True)
    addresses = AddressSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'name', 'phone', 'email', 'addresses']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        name = validated_data.pop('name')
        phone = validated_data.pop('phone', '')
        email = validated_data.pop('email')
        addresses_data = validated_data.pop('addresses', [])

        # Create user
        user = User.objects.create_user(**validated_data)

        # Create customer profile
        customer = Customer.objects.create(user=user, name=name, phone=phone, email=email)

        # Create addresses
        for address_data in addresses_data:
            Address.objects.create(customer=customer, **address_data)

        return user
```

### Register User via API
Create a view to handle user registration.

```python
class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
```

---

## 5️⃣ **Final Routes**
Update your `urls.py` to include the user registration endpoint.
```python
urlpatterns += [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
]
```

---

## ✅ **How It Works**
1. **User Registration (`POST /register/`)**
   - User provides `username`, `password`, `name`, `email`, and optional `addresses`.
   - A `User`, `Customer`, and `Address` are automatically created.
   
2. **Create Customer (`POST /customers/`)**
   - Allows creating a `Customer` and their associated `addresses`.

3. **Get Customer Details (`GET /customers/{id}/`)**
   - Retrieves details of a `Customer`.

4. **Add Address (`POST /addresses/`)**
   - Allows adding an `Address` to an existing `Customer`.

---

## 🎯 **Next Steps**
- Add authentication (`djangorestframework-simplejwt`) for secure login.
- Use `DRF ViewSets` and `Routers` for a cleaner API structure.

Would you like JWT authentication added to this? 🚀