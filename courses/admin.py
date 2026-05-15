from django.contrib import admin
from .models import Course, Lesson


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_at")
    search_fields = ("title",)  # ← нужно для autocomplete
    ordering = ("title",)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "course", "created_at")
    search_fields = ("title",)
    list_filter = ("course",)
    ordering = ("course", "title")
