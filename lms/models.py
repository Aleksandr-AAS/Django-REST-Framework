from django.db import models
from django.conf import settings


class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name="название")
    preview = models.ImageField(
        upload_to="courses/previews/", blank=True, null=True, verbose_name="превью"
    )
    description = models.TextField(blank=True, verbose_name="описание")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses",
        verbose_name="владелец",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "курс"
        verbose_name_plural = "курсы"

    def __str__(self):
        return self.title


class Lesson(models.Model):
    title = models.CharField(max_length=200, verbose_name="название")
    description = models.TextField(blank=True, verbose_name="описание")
    preview = models.ImageField(
        upload_to="lessons/previews/", blank=True, null=True, verbose_name="превью"
    )
    video_link = models.URLField(blank=True, null=True, verbose_name="ссылка на видео")

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="lessons", verbose_name="курс"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="владелец",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "урок"
        verbose_name_plural = "уроки"

    def __str__(self):
        return f"{self.title} (курс: {self.course.title})"
