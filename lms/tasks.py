# from celery import shared_task
# from django.core.mail import send_mail
# from django.conf import settings
# from .models import Course
# # from users.models import Subscription
# from lms.models import Course, Subscription
#
# @shared_task
# def send_course_update_notification(course_id, updated_fields):
#     """
#     Отправляет уведомления всем подписчикам курса об обновлении.
#     """
#     try:
#         course = Course.objects.get(id=course_id)
#         subscribers = Subscription.objects.filter(course=course).select_related('user')
#
#         if not subscribers.exists():
#             return f"No subscribers for course {course.title}"
#
#         subject = f"Обновление курса: {course.title}"
#         message = f"""
#         Здравствуйте!
#
#         Курс "{course.title}" был обновлён.
#
#         Обновлённые разделы: {', '.join(updated_fields)}
#
#         Зайдите на платформу, чтобы посмотреть новые материалы.
#
#         С уважением,
#         Команда LMS
#         """
#
#         recipient_list = [sub.user.email for sub in subscribers]
#
#         send_mail(
#             subject=subject,
#             message=message,
#             from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@lms.com',
#             recipient_list=recipient_list,
#             fail_silently=False,
#         )
#
#         return f"Sent {len(recipient_list)} notifications for course {course.title}"
#
#     except Course.DoesNotExist:
#         return f"Course {course_id} not found"
#     except Exception as e:
#         return f"Error: {str(e)}"

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Course, Subscription


@shared_task
def send_course_update_notification(course_id, updated_fields):
    """
    Отправляет уведомления всем подписчикам курса об обновлении.
    """
    try:
        course = Course.objects.get(id=course_id)
        subscribers = Subscription.objects.filter(course=course).select_related("user")

        if not subscribers.exists():
            return f"No subscribers for course {course.title}"

        subject = f"Обновление курса: {course.title}"
        message = f"""
        Здравствуйте!

        Курс "{course.title}" был обновлён.

        Обновлённые разделы: {', '.join(updated_fields)}

        Зайдите на платформу, чтобы посмотреть новые материалы.

        С уважением,
        Команда LMS
        """

        recipient_list = [sub.user.email for sub in subscribers]

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL or "noreply@lms.com",
            recipient_list=recipient_list,
            fail_silently=False,
        )

        return f"Sent {len(recipient_list)} notifications for course {course.title}"

    except Course.DoesNotExist:
        return f"Course {course_id} not found"
    except Exception as e:
        return f"Error: {str(e)}"
