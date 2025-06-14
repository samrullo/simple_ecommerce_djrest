# How to make dj_rest_auth login return custom user info with customer and addresses

I had to define ```CustomLoginView``` and override ```auth/login/``` in ```urlpatterns```

```python
urlpatterns = [
...,
    path('auth/login/', CustomLoginView.as_view(), name="rest_login"),
    path('auth/', include('dj_rest_auth.urls')),  # Login, Logout, Password Reset
...
]
```

```CustomLoginView``` is defined as below, the key is that I had to override its ```post``` method

```python
class CustomLoginView(LoginView):
    def post(self, request, *args, **kwargs):
        logger.debug("CustomLoginView.post() called")
        # Call the default login view to process authentication
        response = super().post(request, *args, **kwargs)

        # If the login was successful and we have a user, update the response data
        if self.user:
            logger.debug("Modifying response data with custom user details")
            # Replace the default 'user' key with data from your custom serializer
            response.data['user'] = CustomUserSerializer(
                self.user, context=self.get_serializer_context()
            ).data
        else:
            logger.debug("No authenticated user found in the response")
        return response
```

As you can see within overridden ```post``` method, it sets ```user``` response to ```CustomUserSerializer```


```python

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'street', 'city', 'state', 'zip_code', 'country', 'is_default']


class CustomerSerializer(serializers.ModelSerializer):
    # Assuming Customer has a reverse relationship to Address via address_set.
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'phone', 'addresses']  # Add any additional fields from Customer


class CustomUserSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()

    def get_customer(self, obj):
        try:
            customer_obj = obj.customer  # should work if a Customer exists
            return CustomerSerializer(customer_obj).data
        except Exception as e:
            return None

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'customer']
```

With above below curl works

```bash
 curl -X POST http://localhost:8000/auth/login/ -H "Content-Type: application/json"      -d '{"email": "naira@mail.com", "password": "kichk!nasir"}'
```

and it returns below response

```bash
{"access":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM5MjY5MjU5LCJpYXQiOjE3MzkyNjg5NTksImp0aSI6IjhmOTJlZGQxZjViZTQ5ZDU5ZDMyMDJmMjI3NmM2YzBmIiwidXNlcl9
pZCI6NDJ9.q41PCkAecRJZFWVRE-tTEPCYYSg5tel0UJyx5fmp5Mo","refresh":"","user":{"id":42,"username":"naira","email":"naira@mail.com","first_name":"Naira","last_name":"Amrulloeva","customer":{"
id":17,"phone":"1234567890","addresses":[{"id":9,"street":"Ushirohirai 170 ban 315 goshitu","city":"Nagareyama","state":"Chiba","zip_code":"270-0151","country":"Japan","is_default":true}]}}}
```

# Setting access and refresh tokens with TokenObtainPairSerializer

Refer to this conversation https://chatgpt.com/share/684a7964-3430-8010-b2a9-b4e1b0e3fc65