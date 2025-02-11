# How to register custom user

I have ```Customer``` model that maps one to one to django.contrib.auth.models.User and has ```phone``` field.
Then I have ```Address``` model that stores customer address. Customer can have multiple addresses. 
But usually customer has one primary address.


By default ```dj_rest_auth``` calls ```DefaultAccountAdapter```'s ```save_user()``` method.

So we define custom account adapter and custom register serializer. 
Then in settings.py we specify those custom account adapter and custom register serializers

```python
from dj_rest_auth.registration.serializers import RegisterSerializer

class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True, max_length=30)
    last_name = serializers.CharField(required=True, max_length=30)
    customer = CustomerSerializer(required=True)
    address = AddressSerializer(required=True)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        logger.debug(f"cleaned data is : {data}")
        logger.debug(f"validated_data is : {self.validated_data}")
        data['first_name'] = self.validated_data.get('first_name', '')
        data['last_name'] = self.validated_data.get('last_name', '')
        # Include the nested dictionaries for customer and address:
        data['customer'] = self.validated_data.get('customer', {})
        data['address'] = self.validated_data.get('address', {})
        logging.debug(f"data after setting is : {data}")
        return data


# ecommerce/adapters.py

from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        logger.debug("CustomAccountAdapter.save_user() called")
        # First let the parent adapter save the user (this handles basic fields)
        user = super().save_user(request, user, form, commit)

        # Ensure the user is saved (has a primary key) before creating related objects.
        if not user.pk:
            user.save()
            logger.debug("User saved to ensure it has a primary key.")

        # Now, access your custom fields from the form's cleaned_data.
        # Note: If you’re using a custom serializer, you may need to pass these values
        # differently; adjust accordingly.
        extra_data = form.cleaned_data
        customer_data = extra_data.get("customer")
        address_data = extra_data.get("address")
        logger.debug(f"customer data : {customer_data}, address_data : {address_data}")

        if customer_data:
            # Create your Customer instance
            Customer.objects.create(user=user, **customer_data)
            logger.debug("Customer created with: %s", customer_data)
        if address_data:
            # You might need to first ensure the customer exists
            customer = getattr(user, "customer", None)
            if customer:
                Address.objects.create(customer=customer, **address_data)
                logger.debug("Address created with: %s", address_data)

        return user

```

In settings.py

```python
REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'ecommerce.serializers.user.serializers.CustomRegisterSerializer',
}

ACCOUNT_ADAPTER = "ecommerce.serializers.user.serializers.CustomAccountAdapter"
```

We also create CustomRegisterView that will have CustomRegisterSerializer as its serializer.
This way our custom account adapter will get data by calling get_cleaned_data of CustomRegisterSerializer.

```python
from dj_rest_auth.registration.views import RegisterView
from ecommerce.serializers.user.serializers import CustomRegisterSerializer


class CustomRegisterView(RegisterView):
    serializer_class = CustomRegisterSerializer
```

Finally, I had to specify registration urls in below manner for things to work

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('ecommerce/', include('ecommerce.urls')),
    path('api/', include('api.urls')),
    # path('auth/login/', CustomJWTLoginView.as_view(), name="rest_login"),
    path('auth/', include('dj_rest_auth.urls')),  # Login, Logout, Password Reset
    path('auth/registration/account-confirm-email/<str:key>/', CustomVerifyEmailView.as_view(),
         name="account_confirm_email"),
    path('auth/register/', CustomRegisterView.as_view(), name="rest_register"),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),  # Registration + Email Verification

]
```

With that folowing API call works

```bash
curl -X POST http://localhost:8000/auth/register/ -H "Content-Type: application/json" -d '{"email": "naira@mail.com","password1": "kichk!nasir","password2": "kichk!nasir", "first_name":
 "Naira", "last_name": "Amrulloeva", "customer": {"phone": "1234567890"},"address": {"street": "Ushirohirai 170 ban 315 goshitu", "city": "Nagareyama","state": "Chiba","zip_code": "270-0151","country": "Japan","is_default": true}}'
```

it returns response ```{"detail":"Verification e-mail sent."}```

# Why you are checking user.pk and saving user explicitly

Because it turned out ```dj_rest_auth``` calls adapter ```save_user``` method with ```commit=False``` by default.