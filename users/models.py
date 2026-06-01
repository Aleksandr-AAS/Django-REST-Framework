from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)

    phone = models.CharField(
        max_length=35, blank=True, null=True, verbose_name="телефон"
    )
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="город")
    avatar = models.ImageField(
        upload_to="users/avatars/", blank=True, null=True, verbose_name="аватарка"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"
        # Убедитесь, что здесь НЕТ ordering = ['payment_date']
        # Если есть — удалите эту строку

    def __str__(self):
        return self.email


class Payment(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Наличные"
        TRANSFER = "transfer", "Перевод на счет"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Пользователь",
    )
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата оплаты")
    course = models.ForeignKey(
        "lms.Course",
        # "courses.Course",  # ← используем строковую ссылку, чтобы избежать циклического импорта
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="Оплаченный курс",
    )
    lesson = models.ForeignKey(
        "courses.Lesson",  # ← используем строковую ссылку
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="Оплаченный урок",
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Сумма оплаты"
    )
    payment_method = models.CharField(
        max_length=10,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH,
        verbose_name="Способ оплаты",
    )

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ["-payment_date"]  # ← это правильно, здесь ordering

    def __str__(self):
        target = self.course if self.course else self.lesson
        return f"Платеж {self.user} - {target} - {self.amount} руб."

    stripe_session_id = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="ID сессии Stripe"
    )
    stripe_payment_intent_id = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="ID PaymentIntent Stripe"
    )
    payment_link = models.URLField(
        max_length=500, blank=True, null=True, verbose_name="ссылка на оплату"
    )
    is_successful = models.BooleanField(default=False, verbose_name="успешно оплачено")
