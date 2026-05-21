from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Payment
from courses.models import Course, Lesson
from django.contrib.auth import get_user_model

User = get_user_model()


class UserForPaymentSerializer(serializers.ModelSerializer):
    """Пользователь для выпадающего списка"""

    class Meta:
        model = User
        fields = ["id", "email", "phone"]


class CourseForPaymentSerializer(serializers.ModelSerializer):
    """Курс для выпадающего списка"""

    class Meta:
        model = Course
        fields = ["id", "title"]


class LessonForPaymentSerializer(serializers.ModelSerializer):
    """Урок для выпадающего списка"""

    class Meta:
        model = Lesson
        fields = ["id", "title", "course"]


class PaymentSerializer(serializers.ModelSerializer):
    # Поля для вывода информации (при GET запросе)
    user_info = UserForPaymentSerializer(source="user", read_only=True)
    course_info = CourseForPaymentSerializer(source="course", read_only=True)
    lesson_info = LessonForPaymentSerializer(source="lesson", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "user",
            "user_info",
            "payment_date",
            "amount",
            "payment_method",
            "course",
            "course_info",
            "lesson",
            "lesson_info",
        ]


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра/обновления пользователя (только чтение для некоторых полей)"""

    class Meta:
        model = User
        fields = ("id", "email", "phone", "city", "avatar", "is_staff", "date_joined")
        read_only_fields = ("id", "is_staff", "date_joined")


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации нового пользователя"""

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("email", "password", "password2", "phone", "city", "avatar")

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        return user
