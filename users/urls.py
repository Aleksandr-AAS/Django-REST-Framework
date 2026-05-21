from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, UserViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"payments", PaymentViewSet, basename="payment")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path(
        "login/", TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),  # стандартная вьюха
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("", include(router.urls)),
]
