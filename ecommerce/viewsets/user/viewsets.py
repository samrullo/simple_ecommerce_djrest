import logging
from rest_framework import viewsets, permissions
from ecommerce.models import Customer, Address, Role, Staff
from ecommerce.serializers import CustomerSerializer, AddressSerializer, RoleSerializer, StaffSerializer
from dj_rest_auth.registration.views import VerifyEmailView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from allauth.account.utils import send_email_confirmation
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

User = get_user_model()

logger = logging.getLogger(__name__)


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


# ecommerce/views.py
from dj_rest_auth.views import LoginView
from ecommerce.serializers.user.serializers import CustomUserSerializer


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

    def finalize_response(self, request, response, *args, **kwargs):
        logger.debug("CustomLoginView.finalize_response() called")
        return super().finalize_response(request, response, *args, **kwargs)

    def get_response_data(self):
        """
        Return a custom response that includes the user details from CustomUserSerializer.
        """
        # Get the default response data (e.g., tokens)
        logger.debug(f"CustomLoginView was called")
        data = super().get_response_data()

        # If a user is authenticated, override the 'user' key with our custom serialized data.
        if self.user:
            data['user'] = CustomUserSerializer(
                self.user, context=self.get_serializer_context()
            ).data
        return data


class ResendEmailVerificationView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")

        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user's email is already verified
        email_address = EmailAddress.objects.filter(user=user, email=email).first()
        if email_address and email_address.verified:
            return Response({"error": "Email is already verified"}, status=status.HTTP_400_BAD_REQUEST)

        # Resend the verification email
        send_email_confirmation(request, user)

        return Response({"detail": "Verification email has been resent"}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    user = request.user
    serializer = CustomUserSerializer(user)  # Serialize user with CustomUserSerializer
    return Response(serializer.data)
