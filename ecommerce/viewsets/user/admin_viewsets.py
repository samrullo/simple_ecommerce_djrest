import random
import string

from django.contrib.auth import get_user_model
from rest_framework import permissions, serializers, viewsets

from ecommerce.models import Address, Customer

User = get_user_model()


def generate_random_password(length=12):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_unique_email(first_name, last_name):
    base_email = f"{last_name.lower()}.{first_name.lower()}@mail.com"
    email = base_email
    counter = 1
    while User.objects.filter(email=email).exists():
        email = f"{last_name.lower()}.{first_name.lower()}{counter}@mail.com"
        counter += 1
    return email


class EditableAddressSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Address
        fields = ["id", "street", "city", "state", "zip_code", "country", "is_default"]


class EditableCustomerSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)
    email = serializers.EmailField(source="user.email", required=False)
    phone = serializers.CharField(required=False)
    addresses = EditableAddressSerializer(many=True, required=False)

    class Meta:
        model = Customer
        fields = ["id", "first_name", "last_name", "email", "phone", "addresses"]

    def create(self, validated_data):
        user_data = validated_data.pop("user", {})
        email = user_data.get("email") or generate_unique_email(
            user_data.get("first_name", "user"), user_data.get("last_name", "unknown")
        )
        password = generate_random_password()
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=user_data.get("first_name", ""),
            last_name=user_data.get("last_name", ""),
        )
        phone = validated_data.get("phone", "")
        customer = Customer.objects.create(user=user, phone=phone)

        # Create addresses
        address_data_list = validated_data.get("addresses", [])
        for addr_data in address_data_list:
            Address.objects.create(customer=customer, **addr_data)

        return customer

    def update(self, instance, validated_data):
        # Update user fields
        user_data = validated_data.pop("user", {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()

        # Update customer fields
        for attr, value in validated_data.items():
            if attr != "addresses":
                setattr(instance, attr, value)
        instance.save()

        # Update addresses if present
        address_data_list = validated_data.get("addresses", [])
        existing_addresses = {addr.id: addr for addr in instance.addresses.all()}

        updated_ids = set()

        for addr_data in address_data_list:
            addr_id = addr_data.get("id")
            if addr_id and addr_id in existing_addresses:
                # Update existing address
                addr = existing_addresses[addr_id]
                for field, val in addr_data.items():
                    setattr(addr, field, val)
                addr.save()
                updated_ids.add(addr_id)
            else:
                # Create new address
                Address.objects.create(customer=instance, **addr_data)

        # Optionally delete removed addresses
        for addr_id, addr in existing_addresses.items():
            if addr_id not in updated_ids:
                addr.delete()

        return instance


class CustomerAdminViewSet(viewsets.ModelViewSet):
    queryset = (
        Customer.objects.select_related("user").prefetch_related("addresses").all()
    )
    serializer_class = EditableCustomerSerializer
    permission_classes = [permissions.IsAdminUser]
