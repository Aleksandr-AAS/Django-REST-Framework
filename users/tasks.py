# from celery import shared_task
# import time
#
# @shared_task
# def test_task():
#     """Тестовая задача для проверки Celery"""
#     print("✅ Celery работает!")
#     return "Задача"

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()


@shared_task
def block_inactive_users():
    """
    Блокирует пользователей, которые не заходили более месяца.
    """
    # Рассчитываем дату месяц назад
    month_ago = timezone.now() - timedelta(days=30)

    # Находим активных пользователей с last_login старше месяца
    inactive_users = User.objects.filter(is_active=True, last_login__lt=month_ago)

    count = inactive_users.count()

    # Блокируем их
    inactive_users.update(is_active=False)

    message = f"Блокировано {count} неактивных пользователей (последний вход до {month_ago.date()})"
    print(message)
    return message
