# Custom user registration

Yes, you can absolutely leverage your existing `CustomerSerializer` and `AddressSerializer` within your custom registration flow. The idea is to have your custom registration serializer collect the nested data (for customer and address) and then, in your custom account adapter, delegate the creation of these related models to your existing serializers.

Below is an example of how you might implement this:

---

### 1. Define Your Existing Serializers

Let’s assume you already have serializers similar to the following:

```python
# your_app/serializers.py
from rest_framework import serializers
from your_app.models import Customer, Address

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['phone']  # or any other customer fields you want to expose

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['street', 'city', 'state', 'zip_code', 'country', 'is_default']
```

*Note:* Adjust the fields as necessary for your use case.

---

### 2. Create a Custom Registration Serializer with Nested Fields

You can modify your custom registration serializer to include nested fields for customer and address. For example:

```python
# your_app/registration_serializers.py
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from your_app.serializers import CustomerSerializer, AddressSerializer

class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True, max_length=30)
    last_name = serializers.CharField(required=True, max_length=30)
    # Instead of flat fields for phone/address, nest the data using your serializers.
    customer = CustomerSerializer(required=True)
    address = AddressSerializer(required=True)

    def get_cleaned_data(self):
        """
        Combine the base cleaned data with the extra nested data.
        """
        data = super().get_cleaned_data()
        data.update({
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            # The nested serializers already validate and return dictionaries.
            'customer': self.validated_data.get('customer', {}),
            'address': self.validated_data.get('address', {})
        })
        return data
```

**Key Points:**

- The `customer` and `address` fields are defined as nested serializers.  
- The incoming JSON must provide nested objects for these fields. For example:

  ```json
  {
    "email": "dinara@mail.com",
    "password1": "thepassword",
    "password2": "thepassword",
    "first_name": "Dinara",
    "last_name": "Smith",
    "customer": {
        "phone": "1234567890"
    },
    "address": {
        "street": "123 Main St",
        "city": "Hometown",
        "state": "CA",
        "zip_code": "90210",
        "country": "USA",
        "is_default": true
    }
  }
  ```

- The `get_cleaned_data()` method bundles these nested dictionaries along with the other fields so they can be accessed in the adapter.

---

### 3. Create a Custom Account Adapter that Uses the Existing Serializers

Override the account adapter’s `save_user()` method to handle the creation of the related models using your existing serializers:

```python
# your_app/adapters.py
from allauth.account.adapter import DefaultAccountAdapter
from your_app.models import Customer, Address
from your_app.serializers import CustomerSerializer, AddressSerializer

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        """
        Save the user, then create the Customer and Address using nested serializers.
        """
        # Save the basic User instance.
        user = super().save_user(request, user, form, commit=False)
        data = form.cleaned_data
        user.first_name = data.get('first_name', '')
        user.last_name = data.get('last_name', '')
        if commit:
            user.save()
        
        # Prepare and create the Customer instance.
        customer_data = data.get('customer', {})
        # You may pass the user instance directly or its id based on your serializer's implementation.
        customer_data['user'] = user.pk  
        customer_serializer = CustomerSerializer(data=customer_data)
        customer_serializer.is_valid(raise_exception=True)
        customer = customer_serializer.save()
        
        # Prepare and create the Address instance.
        address_data = data.get('address', {})
        # Associate the address with the newly created customer.
        address_data['customer'] = customer.pk  
        address_serializer = AddressSerializer(data=address_data)
        address_serializer.is_valid(raise_exception=True)
        address_serializer.save()
        
        return user
```

**Notes:**

- After saving the user (and updating `first_name` and `last_name`), the adapter retrieves the nested data for customer and address.
- It adds a reference to the user (for the Customer) and to the customer (for the Address) before instantiating the existing serializers.
- The serializers’ `is_valid(raise_exception=True)` call ensures that if there’s any validation error in the nested data, it’s properly raised.
- Finally, the nested objects are saved using their respective serializers.

---

### 4. Update Your Settings

Tell dj‑rest‑auth and django‑allauth to use your custom serializers and adapter by updating your settings:

```python
# settings.py

REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'your_app.registration_serializers.CustomRegisterSerializer',
}

ACCOUNT_ADAPTER = 'your_app.adapters.CustomAccountAdapter'
```

Replace `"your_app"` with the actual name of your Django app.

---

### How It Works Together

1. **Client Request:**  
   A client sends a registration POST with nested JSON data for both the customer (e.g., phone) and the default address.

2. **Validation:**  
   The `CustomRegisterSerializer` validates the data using the nested `CustomerSerializer` and `AddressSerializer` along with the extra user fields.  
   The `get_cleaned_data()` method aggregates all this validated data.

3. **User Creation:**  
   In the custom account adapter’s `save_user()` method, after the user instance is saved, the nested data is used to create a `Customer` and then an `Address` instance by delegating to your existing serializers.

4. **Result:**  
   The user is registered with the extra fields, and the related models are populated accordingly.

---

### Summary

- **Nested Serializers:**  
  Your custom registration serializer includes nested fields for customer and address using your existing `CustomerSerializer` and `AddressSerializer`.

- **Adapter Logic:**  
  The custom account adapter extracts the nested data from the cleaned data, adds necessary foreign key references, and then uses your existing serializers to validate and create the `Customer` and `Address` instances.

This approach allows you to reuse your existing serializers and keep your registration logic modular and DRY.