import re
from rest_framework import serializers


def validate_youtube_link(value):
    """
    Валидатор для проверки, что ссылка ведёт на youtube.com
    """
    if not value:
        return value

    # Регулярное выражение для проверки youtube ссылок
    youtube_patterns = [
        r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/",
        r"(https?://)?(www\.)?(m\.youtube\.com)/",
    ]

    is_youtube = False
    for pattern in youtube_patterns:
        if re.match(pattern, value, re.IGNORECASE):
            is_youtube = True
            break

    if not is_youtube:
        raise serializers.ValidationError(
            "Разрешены только ссылки на YouTube (youtube.com или youtu.be)"
        )

    return value


class YouTubeLinkValidator:
    """
    Класс-валидатор для проверки ссылок на YouTube
    """

    def __init__(self, field="video_link"):
        self.field = field

    def __call__(self, attrs):
        """
        Проверка на уровне всего объекта (для Meta.validators)
        """
        value = attrs.get(self.field)
        if value:
            validate_youtube_link(value)
        return attrs

    def __call_single__(self, value):
        """
        Для использования в поле сериализатора
        """
        return validate_youtube_link(value)
