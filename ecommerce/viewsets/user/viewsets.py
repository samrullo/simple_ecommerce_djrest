from rest_framework import viewsets, permissions
from ecommerce.models import Customer, Address, Role, Staff
from ecommerce.serializers import CustomerSerializer, AddressSerializer, RoleSerializer, StaffSerializer
from dj_rest_auth.registration.views import VerifyEmailView
from rest_framework.response import Response
from rest_framework import status


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAdminUser]


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAdminUser]


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAdminUser]


class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [permissions.IsAdminUser]


class CustomVerifyEmailView(VerifyEmailView):
    def get(self, *args, **kwargs):
        self.object = self.get_object()  # Fetch the email confirmation object
        self.object.confirm(self.request)  # Confirm the email
        return Response({"detail": "Email confirmed"}, status=status.HTTP_200_OK)


# ecommerce/views.py (or another appropriate module)
from dj_rest_auth.registration.views import RegisterView
from ecommerce.serializers.user.serializers import CustomRegisterSerializer


class CustomRegisterView(RegisterView):
    serializer_class = CustomRegisterSerializer