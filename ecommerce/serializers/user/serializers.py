import logging
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from ecommerce.models import Customer, Address, Role, Staff
from django.contrib.auth import get_user_model
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailConfirmation

logger = logging.getLogger(__name__)

User = get_user_model()


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["id", "street", "city", "state", "zip_code", "country", "is_default"]


class CustomerSerializer(serializers.ModelSerializer):
    # Assuming Customer has a reverse relationship to Address via address_set.
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = Customer
        fields = ["id", "phone", "addresses"]  # Add any additional fields from Customer


class CustomerWithUserSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer()
    addresses = AddressSerializer(many=True)

    class Meta:
        model = Customer
        fields = ["id", "phone", "user", "addresses"]


class CustomUserSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()

    def get_customer(self, obj):
        try:
            customer_obj = obj.customer  # should work if a Customer exists
            return CustomerSerializer(customer_obj).data
        except Exception:
            return None

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_superuser",
            "customer",
        ]


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"


class StaffSerializer(serializers.ModelSerializer):
    # Represent the related user as a string.
    user = serializers.StringRelatedField()
    role = RoleSerializer(read_only=True)

    class Meta:
        model = Staff
        fields = "__all__"


class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True, max_length=30)
    last_name = serializers.CharField(required=True, max_length=30)
    customer = CustomerSerializer(required=True)
    address = AddressSerializer(required=True)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        logger.debug(f"cleaned data is : {data}")
        logger.debug(f"validated_data is : {self.validated_data}")
        data["first_name"] = self.validated_data.get("first_name", "")
        data["last_name"] = self.validated_data.get("last_name", "")
        # Include the nested dictionaries for customer and address:
        data["customer"] = self.validated_data.get("customer", {})
        data["address"] = self.validated_data.get("address", {})
        logging.debug(f"data after setting is : {data}")
        return data


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

    def send_confirmation_mail(
            self, request, emailconfirmation: EmailConfirmation, signup
    ):
        """
        Override the confirmation link sent in the email.
        """
        logger.debug("CustomAccountAdapter.send_confirmation_mail called")

        # 🔗 Build a link to your React frontend
        react_link = f"http://localhost:3000/verify-email/{emailconfirmation.key}"
        logger.debug(f"Generated react verification link: {react_link}")

        ctx = {
            "user": emailconfirmation.email_address.user,
            "activate_url": react_link,
            "current_site": None,
            "key": emailconfirmation.key,
        }
        self.send_mail(
            "account/email/email_confirmation",
            emailconfirmation.email_address.email,
            ctx,
        )

    # def confirm_email(self, request, email_address):
    #     logger.debug(f"Confirming email for: {email_address.email}")
    #
    #     # ✅ Explicitly mark as verified
    #     email_address.verified = True
    #     email_address.save()
    #
    #     # ✅ Optionally set user on request
    #     request.user = email_address.user
    #     logger.debug(f"Email marked as verified for user: {email_address.user}")
