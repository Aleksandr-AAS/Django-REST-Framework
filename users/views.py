from rest_framework import viewsets, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from .models import Payment
from .serializers import (
    PaymentSerializer,
    UserSerializer,
    UserCreateSerializer,
)
from .filters import PaymentFilter

User = get_user_model()


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


class RegisterView(generics.CreateAPIView):
    """Регистрация пользователя (доступно всем)"""

    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD для пользователей:
    - GET /users/ - список (только для админа)
    - GET /users/{id}/ - детали (только админ или владелец)
    - PATCH /users/{id}/ - обновить
    - DELETE /users/{id}/ - удалить
    - GET /users/me/ - свой профиль
    - PATCH /users/me/ - обновить свой профиль
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=user.id)

    @action(detail=False, methods=["get", "patch"], url_path="me")
    def me(self, request):
        """Получить или обновить свой профиль"""
        user = request.user
        if request.method == "PATCH":
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(user)
        return Response(serializer.data)
