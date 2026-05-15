from rest_framework import serializers
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
