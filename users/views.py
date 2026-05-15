from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Payment
from .serializers import PaymentSerializer
from .filters import PaymentFilter


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related("user", "course", "lesson").all()
    serializer_class = PaymentSerializer

    # Настройка фильтрации и сортировки
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter

    # Доступные поля для сортировки
    ordering_fields = ["payment_date", "amount", "user__email"]

    # Сортировка по умолчанию (сначала новые)
    ordering = ["-payment_date"]
