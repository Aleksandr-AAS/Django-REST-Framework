from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Кастомный сериализатор для авторизации по email"""

    # Переопределяем поле username на email
    username_field = "email"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Заменяем поле username на email
        self.fields["email"] = serializers.EmailField()
        # Удаляем username из полей, если он есть
        if "username" in self.fields:
            del self.fields["username"]
