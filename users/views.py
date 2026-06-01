from rest_framework import viewsets, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
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
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiTypes
from .services import (
    create_stripe_product,
    create_stripe_price,
    create_checkout_session,
)
from lms.models import Course
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers_jwt import CustomTokenObtainPairSerializer
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """Получение JWT токена (логин)"""

    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    """Обновление JWT токена"""

    pass


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


class InitiatePaymentView(APIView):
    """Эндпоинт для создания платежа и получения ссылки на оплату"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Создать платёж на курс",
        description="Создаёт платёж в Stripe и возвращает ссылку на оплату",
        tags=["payments"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "course_id": {
                        "type": "integer",
                        "description": "ID курса для оплаты",
                    },
                },
                "required": ["course_id"],
            }
        },
        responses={
            201: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    )
    def post(self, request):
        user = request.user
        course_id = request.data.get("course_id")

        if not course_id:
            return Response(
                {"error": "course_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        course = get_object_or_404(Course, id=course_id)
        amount = 1000  # Здесь можно брать цену из модели курса

        # 1. Создаём продукт и цену в Stripe
        stripe_product = create_stripe_product(course)
        stripe_price = create_stripe_price(stripe_product.id, amount)

        # 2. URL для возврата после оплаты
        base_url = request.build_absolute_uri("/")
        success_url = (
            f"{base_url}api/payment-success/?session_id={{CHECKOUT_SESSION_ID}}"
        )
        cancel_url = f"{base_url}api/payment-cancel/"

        # 3. Создаём сессию Stripe Checkout
        checkout_session = create_checkout_session(
            stripe_price.id, success_url, cancel_url
        )

        # 4. Сохраняем платёж в БД
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=amount,
            payment_method="stripe",
            stripe_session_id=checkout_session.id,
            payment_link=checkout_session.url,
        )

        return Response(
            {
                "payment_id": payment.id,
                "payment_link": checkout_session.url,
                "session_id": checkout_session.id,
            },
            status=status.HTTP_201_CREATED,
        )


@csrf_exempt
def payment_success_view(request):
    session_id = request.GET.get("session_id")
    return HttpResponse(f"Оплата успешно завершена! Session ID: {session_id}")


@csrf_exempt
def payment_cancel_view(request):
    return HttpResponse("Оплата отменена.")
