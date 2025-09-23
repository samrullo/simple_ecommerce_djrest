from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import DummyProduct, DummyProductSerializer


class DummyProductViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        dummy_products = [
            DummyProduct("MacBook", "Apple personal computing device", 500000),
            DummyProduct("iPhone", "Apple mobile device", 200000),
        ]
        dummy_products_serializer = DummyProductSerializer(dummy_products, many=True)
        return Response({"results": dummy_products_serializer.data})


from dj_rest_auth.serializers import UserDetailsSerializer
from dj_rest_auth.views import LoginView
from rest_framework_simplejwt.tokens import RefreshToken


class CustomJWTLoginView(LoginView):
    def get_response_data(self):
        """
        Instead of returning self.token (which is a Token instance),
        generate JWT tokens using SimpleJWT's RefreshToken.for_user.
        """
        # Generate a refresh token for the authenticated user.
        refresh = RefreshToken.for_user(self.user)
        # Return a dict with the access token, refresh token, and serialized user data.
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserDetailsSerializer(
                self.user, context=self.get_serializer_context()
            ).data,
        }
