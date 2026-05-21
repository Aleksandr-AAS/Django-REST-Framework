from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModeratorOrOwner, NotIsModerator


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для курсов:
    - Модераторы: просмотр и редактирование любых курсов, НО НЕ создание и удаление
    - Обычные пользователи: только свои курсы (просмотр, редактирование, удаление)
    - Админы: всё
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action == "create":
            # Создание: только НЕ модераторы (обычные пользователи и админы)
            return [IsAuthenticated(), NotIsModerator()]
        elif self.action == "destroy":
            # Удаление: только владелец или админ (но не модератор)
            return [IsAuthenticated(), IsModeratorOrOwner()]
        else:
            # Просмотр и редактирование: модераторы или владельцы
            return [IsAuthenticated(), IsModeratorOrOwner()]

    def perform_create(self, serializer):
        # При создании привязываем владельца
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Course.objects.none()

        # Модераторы и админы видят все курсы
        if user.groups.filter(name="moderators").exists() or user.is_staff:
            return Course.objects.all()

        # Обычные пользователи видят только свои курсы
        return Course.objects.filter(owner=user)


class LessonListCreateView(generics.ListCreateAPIView):
    """
    Список уроков и создание:
    - Создавать могут только НЕ модераторы
    - Просмотр списка: модераторы видят все, обычные — только свои
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            # Создание: только НЕ модераторы
            return [IsAuthenticated(), NotIsModerator()]
        # Просмотр списка: модераторы или владельцы
        return [IsAuthenticated(), IsModeratorOrOwner()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Lesson.objects.none()

        # Модераторы и админы видят все уроки
        if user.groups.filter(name="moderators").exists() or user.is_staff:
            return Lesson.objects.all()

        # Обычные пользователи видят только уроки своих курсов
        return Lesson.objects.filter(course__owner=user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Получение, обновление, удаление урока:
    - Модераторы: просмотр и редактирование любых уроков, НО НЕ удаление
    - Обычные пользователи: только свои уроки
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModeratorOrOwner]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Lesson.objects.none()

        if user.groups.filter(name="moderators").exists() or user.is_staff:
            return Lesson.objects.all()

        return Lesson.objects.filter(owner=user)
