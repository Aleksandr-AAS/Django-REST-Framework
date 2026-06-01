from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    UserViewSet,
    PaymentViewSet,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    InitiatePaymentView,
)
from .views import payment_success_view, payment_cancel_view

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"payments", PaymentViewSet, basename="payment")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("pay/", InitiatePaymentView.as_view(), name="initiate-payment"),
    path("payment-success/", payment_success_view, name="payment-success"),
    path("payment-cancel/", payment_cancel_view, name="payment-cancel"),
    path("", include(router.urls)),
]
