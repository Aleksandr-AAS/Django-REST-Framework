from rest_framework import viewsets
from .models import Course
from .serializers import CourseSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.prefetch_related("lessons").all()  # ← оптимизация
    serializer_class = CourseSerializer
