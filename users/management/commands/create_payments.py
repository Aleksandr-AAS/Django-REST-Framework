from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decimal import Decimal
from users.models import Payment
from courses.models import Course, Lesson

User = get_user_model()


class Command(BaseCommand):
    help = "Создаёт тестовые платежи для пользователей"

    def handle(self, *args, **options):
        # Проверяем, есть ли пользователи
        if not User.objects.exists():
            self.stdout.write(
                self.style.ERROR(
                    "❌ Нет пользователей. Сначала создай пользователя"
                    + " (например, через admin или createsuperuser)"
                )
            )
            return

        # Проверяем, есть ли курсы или уроки
        if not Course.objects.exists() and not Lesson.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    "⚠️ Нет ни курсов, ни уроков. "
                    "Платежи будут созданы без привязки к ним."
                )
            )

        user = User.objects.first()

        # Платёж за курс
        course = Course.objects.first()
        if course:
            Payment.objects.get_or_create(
                user=user,
                course=course,
                defaults={
                    "amount": Decimal("2500.00"),
                    "payment_method": "transfer",
                },
            )
            self.stdout.write(self.style.SUCCESS(f"✅ Платёж за курс: {course.title}"))
        else:
            self.stdout.write(self.style.WARNING("⚠️ Нет ни одного курса"))

        # Платёж за урок
        lesson = Lesson.objects.first()
        if lesson:
            Payment.objects.get_or_create(
                user=user,
                lesson=lesson,
                defaults={
                    "amount": Decimal("800.00"),
                    "payment_method": "cash",
                },
            )
            self.stdout.write(self.style.SUCCESS(f"✅ Платёж за урок: {lesson.title}"))
        else:
            self.stdout.write(self.style.WARNING("⚠️ Нет ни одного урока"))

        # Ещё один платеж за курс, если есть
        if course and Course.objects.count() >= 1:
            Payment.objects.get_or_create(
                user=user,
                course=course,
                defaults={
                    "amount": Decimal("3200.00"),
                    "payment_method": "cash",
                },
            )
            self.stdout.write(
                self.style.SUCCESS(f"✅ Повторный платёж за курс: {course.title}")
            )

        self.stdout.write(
            self.style.SUCCESS("\n🎉 Команда выполнена. Платежи созданы!")
        )
