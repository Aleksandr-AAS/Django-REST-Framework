from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from lms.models import Course, Lesson, Subscription

User = get_user_model()


class LessonCRUDTestCase(TestCase):
    """
    Тесты для CRUD операций с уроками
    """

    def setUp(self):
        """
        Подготовка тестовых данных перед каждым тестом
        """
        # Создаем группы
        self.moderator_group, _ = Group.objects.get_or_create(name="moderators")

        # Создаем пользователей
        self.user = User.objects.create_user(
            email="user@test.ru",
            password="Qwerty123",
            phone="+79123456789",
            city="Москва",
        )

        self.moderator = User.objects.create_user(
            email="moderator@test.ru", password="Qwerty123"
        )
        self.moderator.groups.add(self.moderator_group)

        self.admin = User.objects.create_superuser(
            email="admin@test.ru", password="Qwerty123"
        )

        # Создаем курс
        self.course = Course.objects.create(
            title="Тестовый курс",
            description="Описание тестового курса",
            owner=self.user,
        )

        # Создаем урок
        self.lesson = Lesson.objects.create(
            title="Тестовый урок",
            description="Описание тестового урока",
            video_link="https://www.youtube.com/watch?v=abc123",
            course=self.course,
            owner=self.user,
        )

        # Настраиваем API клиент
        self.client = APIClient()

        # URL для API
        self.lessons_list_url = reverse("lesson-list-create")
        self.lesson_detail_url = reverse("lesson-detail", args=[self.lesson.id])

    def test_create_lesson_by_owner_success(self):
        """Тест: владелец может создать урок в своем курсе"""
        self.client.force_authenticate(user=self.user)

        data = {
            "title": "Новый урок",
            "description": "Описание нового урока",
            "video_link": "https://www.youtube.com/watch?v=xyz789",
            "course": self.course.id,
        }

        response = self.client.post(self.lessons_list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)
        self.assertEqual(response.data["title"], "Новый урок")
        self.assertEqual(response.data["owner"], self.user.id)

    def test_create_lesson_by_moderator_forbidden(self):
        """Тест: модератор НЕ может создать урок"""
        self.client.force_authenticate(user=self.moderator)

        data = {
            "title": "Урок от модератора",
            "description": "Попытка создания урока модератором",
            "video_link": "https://www.youtube.com/watch?v=xyz789",
            "course": self.course.id,
        }

        response = self.client.post(self.lessons_list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lesson.objects.count(), 1)

    def test_create_lesson_by_admin_success(self):
        """Тест: администратор может создать урок в любом курсе"""
        self.client.force_authenticate(user=self.admin)

        data = {
            "title": "Урок от админа",
            "description": "Создание урока администратором",
            "video_link": "https://www.youtube.com/watch?v=admin123",
            "course": self.course.id,
        }

        response = self.client.post(self.lessons_list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_create_lesson_with_invalid_youtube_link(self):
        """Тест: нельзя создать урок со ссылкой не на YouTube"""
        self.client.force_authenticate(user=self.user)

        invalid_links = [
            "https://rutube.ru/video/123",
            "https://vimeo.com/456",
            "https://google.com",
            "https://yandex.ru",
        ]

        for link in invalid_links:
            data = {
                "title": "Урок с неверной ссылкой",
                "description": "Описание",
                "video_link": link,
                "course": self.course.id,
            }

            response = self.client.post(self.lessons_list_url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("video_link", response.data)

    def test_list_lessons_by_owner(self):
        """Тест: владелец видит только свои уроки"""
        # Создаем урок другого пользователя
        other_user = User.objects.create_user(
            email="other@test.ru", password="Qwerty123"
        )
        other_course = Course.objects.create(
            title="Курс другого пользователя", description="Описание", owner=other_user
        )
        Lesson.objects.create(
            title="Урок другого пользователя",
            description="Описание",
            video_link="https://www.youtube.com/watch?v=other",
            course=other_course,
            owner=other_user,
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.lessons_list_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Пользователь видит только свой урок
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Тестовый урок")

    def test_list_lessons_by_moderator(self):
        """Тест: модератор видит все уроки"""
        # Создаем урок другого пользователя
        other_user = User.objects.create_user(
            email="other@test.ru", password="Qwerty123"
        )
        other_course = Course.objects.create(
            title="Курс другого пользователя", description="Описание", owner=other_user
        )
        Lesson.objects.create(
            title="Урок другого пользователя",
            description="Описание",
            video_link="https://www.youtube.com/watch?v=other",
            course=other_course,
            owner=other_user,
        )

        self.client.force_authenticate(user=self.moderator)
        response = self.client.get(self.lessons_list_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Модератор видит все уроки (2 штуки)
        self.assertEqual(len(response.data["results"]), 2)

    def test_update_lesson_by_owner_success(self):
        """Тест: владелец может обновить свой урок"""
        self.client.force_authenticate(user=self.user)

        data = {"title": "Обновленный урок", "description": "Новое описание"}

        response = self.client.patch(self.lesson_detail_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Обновленный урок")
        self.assertEqual(response.data["description"], "Новое описание")

    def test_update_lesson_by_moderator_success(self):
        """Тест: модератор может обновить чужой урок"""
        self.client.force_authenticate(user=self.moderator)

        data = {"title": "Урок отредактирован модератором"}

        response = self.client.patch(self.lesson_detail_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Урок отредактирован модератором")

    def test_update_lesson_by_other_user_forbidden(self):
        """Тест: другой пользователь не может обновить чужой урок"""
        other_user = User.objects.create_user(
            email="other@test.ru", password="Qwerty123"
        )

        self.client.force_authenticate(user=other_user)

        data = {"title": "Попытка редактирования"}

        response = self.client.patch(self.lesson_detail_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_lesson_by_owner_success(self):
        """Тест: владелец может удалить свой урок"""
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(self.lesson_detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_delete_lesson_by_moderator_forbidden(self):
        """Тест: модератор НЕ может удалить урок"""
        self.client.force_authenticate(user=self.moderator)

        response = self.client.delete(self.lesson_detail_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lesson.objects.count(), 1)

    def test_delete_lesson_by_admin_success(self):
        """Тест: администратор может удалить любой урок"""
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(self.lesson_detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_unauthenticated_user_cannot_access_lessons(self):
        """Тест: неавторизованный пользователь не может получить список уроков"""
        self.client.force_authenticate(user=None)

        response = self.client.get(self.lessons_list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SubscriptionTestCase(TestCase):
    """
    Тесты для функционала подписки на обновления курса
    """

    def setUp(self):
        """
        Подготовка тестовых данных
        """
        # Создаем пользователей
        self.user = User.objects.create_user(email="user@test.ru", password="Qwerty123")

        self.other_user = User.objects.create_user(
            email="other@test.ru", password="Qwerty123"
        )

        # Создаем курсы
        self.course1 = Course.objects.create(
            title="Курс 1", description="Описание курса 1", owner=self.user
        )

        self.course2 = Course.objects.create(
            title="Курс 2", description="Описание курса 2", owner=self.user
        )

        # Настраиваем API клиент
        self.client = APIClient()

        # URL для подписок
        self.subscribe_url = reverse("subscribe")

    def test_subscribe_to_course_success(self):
        """Тест: пользователь может подписаться на курс"""
        self.client.force_authenticate(user=self.user)

        data = {"course_id": self.course1.id}
        response = self.client.post(self.subscribe_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка добавлена")
        self.assertEqual(response.data["is_subscribed"], True)
        self.assertEqual(response.data["course_id"], self.course1.id)

        # Проверяем, что подписка создалась в БД
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course1).exists()
        )

    def test_unsubscribe_from_course_success(self):
        """Тест: пользователь может отписаться от курса"""
        # Сначала подписываемся
        Subscription.objects.create(user=self.user, course=self.course1)

        self.client.force_authenticate(user=self.user)

        data = {"course_id": self.course1.id}
        response = self.client.post(self.subscribe_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка удалена")
        self.assertEqual(response.data["is_subscribed"], False)

        # Проверяем, что подписка удалена из БД
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course1).exists()
        )

    def test_subscribe_toggle_twice(self):
        """Тест: повторная подписка переключает состояние"""
        self.client.force_authenticate(user=self.user)

        data = {"course_id": self.course1.id}

        # Первый раз - подписываемся
        response1 = self.client.post(self.subscribe_url, data, format="json")
        self.assertEqual(response1.data["message"], "Подписка добавлена")
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course1).exists()
        )

        # Второй раз - отписываемся
        response2 = self.client.post(self.subscribe_url, data, format="json")
        self.assertEqual(response2.data["message"], "Подписка удалена")
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course1).exists()
        )

    def test_subscribe_to_nonexistent_course(self):
        """Тест: подписка на несуществующий курс возвращает 404"""
        self.client.force_authenticate(user=self.user)

        data = {"course_id": 99999}
        response = self.client.post(self.subscribe_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_subscribe_without_course_id(self):
        """Тест: запрос без course_id возвращает ошибку"""
        self.client.force_authenticate(user=self.user)

        data = {}
        response = self.client.post(self.subscribe_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_get_subscriptions_list(self):
        """Тест: получение списка подписок пользователя"""
        # Создаем подписки
        Subscription.objects.create(user=self.user, course=self.course1)
        Subscription.objects.create(user=self.user, course=self.course2)

        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.subscribe_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # Проверяем, что в ответе правильные курсы
        course_ids = [item["course_id"] for item in response.data]
        self.assertIn(self.course1.id, course_ids)
        self.assertIn(self.course2.id, course_ids)

    def test_subscription_appears_in_course_detail(self):
        """Тест: в деталях курса появляется признак подписки"""
        self.client.force_authenticate(user=self.user)

        # Подписываемся на курс
        Subscription.objects.create(user=self.user, course=self.course1)

        # Проверяем детали курса
        course_detail_url = reverse("course-detail", args=[self.course1.id])
        response = self.client.get(course_detail_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_subscribed"])

        # Проверяем курс, на который не подписан
        course_detail_url2 = reverse("course-detail", args=[self.course2.id])
        response2 = self.client.get(course_detail_url2, format="json")

        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertFalse(response2.data["is_subscribed"])

    def test_unauthenticated_user_cannot_subscribe(self):
        """Тест: неавторизованный пользователь не может подписаться"""
        self.client.force_authenticate(user=None)

        data = {"course_id": self.course1.id}
        response = self.client.post(self.subscribe_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_get_subscriptions(self):
        """Тест: неавторизованный пользователь не может получить список подписок"""
        self.client.force_authenticate(user=None)

        response = self.client.get(self.subscribe_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_cannot_subscribe_to_nonexistent_course(self):
        """Тест: подписка на несуществующий курс"""
        self.client.force_authenticate(user=self.user)

        data = {"course_id": 999}
        response = self.client.post(self.subscribe_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
