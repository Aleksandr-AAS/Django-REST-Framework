from rest_framework import serializers
from .models import Course, Lesson
from .validators import validate_youtube_link, YouTubeLinkValidator
from .models import Subscription


class LessonSerializer(serializers.ModelSerializer):
    # Способ 1: валидатор на уровне поля
    video_link = serializers.URLField(
        required=False,
        allow_blank=True,
        validators=[validate_youtube_link],  # ← добавляем валидатор
    )

    class Meta:
        model = Lesson
        fields = "__all__"
        # Способ 2: валидатор на уровне объекта (если нужно несколько полей)
        validators = [YouTubeLinkValidator(field="video_link")]


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.IntegerField(source="lessons.count", read_only=True)
    lessons = LessonSerializer(source="lessons.all", many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()  # ← добавляем поле подписки

    class Meta:
        model = Course
        fields = "__all__"
        read_only_fields = ("owner",)

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на курс"""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user, course=obj).exists()
        return False


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки"""

    class Meta:
        model = Subscription
        fields = ("id", "user", "course", "created_at")
        read_only_fields = ("id", "created_at")
