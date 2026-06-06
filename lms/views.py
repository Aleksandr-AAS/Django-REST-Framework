from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Course, Lesson, Subscription
from .serializers import CourseSerializer, LessonSerializer
from .paginators import CoursePaginator, LessonPaginator  # ← импортируем пагинаторы
from users.permissions import IsModeratorOrOwner, NotIsModerator


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для курсов с пагинацией
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CoursePaginator  # ← добавляем пагинатор

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), NotIsModerator()]
        elif self.action == "destroy":
            return [IsAuthenticated(), IsModeratorOrOwner()]
        else:
            return [IsAuthenticated(), IsModeratorOrOwner()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Course.objects.none()

        if user.groups.filter(name="moderators").exists() or user.is_staff:
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def perform_update(self, serializer):
        """
        При обновлении курса запускаем Celery-задачу для рассылки уведомлений.
        """
        course = self.get_object()
        old_data = {
            "title": course.title,
            "description": course.description,
        }

        serializer.save()

        # Определяем, какие поля изменились
        updated_fields = []
        for field, old_value in old_data.items():
            if getattr(course, field) != old_value:
                updated_fields.append(field)

        # Если есть изменения — отправляем задачу
        if updated_fields:
            send_course_update_notification.delay(course.id, updated_fields)


class LessonListCreateView(generics.ListCreateAPIView):
    """
    Список уроков с пагинацией и создание урока
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = LessonPaginator  # ← добавляем пагинатор

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), NotIsModerator()]
        return [IsAuthenticated(), IsModeratorOrOwner()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Lesson.objects.none()

        if user.groups.filter(name="moderators").exists() or user.is_staff:
            return Lesson.objects.all()
        return Lesson.objects.filter(course__owner=user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Получение, обновление и удаление урока
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModeratorOrOwner]


class SubscriptionAPIView(APIView):
    """
    Эндпоинт для управления подписками
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        course_id = request.data.get("course_id")

        if not course_id:
            return Response(
                {"error": "Не указан ID курса"}, status=status.HTTP_400_BAD_REQUEST
            )

        course = get_object_or_404(Course, id=course_id)
        subscription = Subscription.objects.filter(user=user, course=course)

        if subscription.exists():
            subscription.delete()
            message = "Подписка удалена"
            is_subscribed = False
        else:
            Subscription.objects.create(user=user, course=course)
            message = "Подписка добавлена"
            is_subscribed = True

        return Response(
            {
                "message": message,
                "is_subscribed": is_subscribed,
                "course_id": course.id,
                "course_title": course.title,
            },
            status=status.HTTP_200_OK,
        )

    def get(self, request):
        user = request.user
        subscriptions = Subscription.objects.filter(user=user).select_related("course")
        data = [
            {
                "id": sub.id,
                "course_id": sub.course.id,
                "course_title": sub.course.title,
                "created_at": sub.created_at,
            }
            for sub in subscriptions
        ]
        return Response(data, status=status.HTTP_200_OK)
