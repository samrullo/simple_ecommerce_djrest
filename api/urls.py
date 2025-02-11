from rest_framework.routers import DefaultRouter
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import DummyProductViewset

router = DefaultRouter()
router.register(r"product", DummyProductViewset, "products")

urlpatterns = [path("v1/api/", include(router.urls)),
               path("v1/api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
               path("v1/api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh")]
