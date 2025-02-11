import logging
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from ecommerce.models import Customer, Address, Role, Staff
from django.contrib.auth import get_user_model
from allauth.account.adapter import DefaultAccountAdapter

logger = logging.getLogger(__name__)
logger.debug("Loading CustomRegisterSerializer module")


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['phone']  # Exclude the user field from client input

    def create(self, validated_data):
        # Retrieve the user from the context.
        user = self.context.get('user')
        if not user:
            raise serializers.ValidationError("User must be provided in the serializer context.")
        # Create and return the Customer instance.
        return Customer.objects.create(user=user, **validated_data)


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['street', 'city', 'state', 'zip_code', 'country', 'is_default']

    def create(self, validated_data):
        # Get the customer object from the serializer context.
        customer = self.context.get('customer')
        if not customer:
            raise serializers.ValidationError("Customer must be provided in the serializer context.")
        # Create and return the Address instance linked to the provided customer.
        return Address.objects.create(customer=customer, **validated_data)


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class StaffSerializer(serializers.ModelSerializer):
    # Represent the related user as a string.
    user = serializers.StringRelatedField()
    role = RoleSerializer(read_only=True)

    class Meta:
        model = Staff
        fields = '__all__'


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
        logging.debug(f"commit is {commit}")
        user = super().save_user(request, user, form, commit=True)

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
