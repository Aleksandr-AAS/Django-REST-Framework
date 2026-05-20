from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """Проверка, является ли пользователь модератором"""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name="moderators").exists()


class IsOwner(permissions.BasePermission):
    """Проверка, является ли пользователь владельцем объекта"""

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        # Проверяем, есть ли у объекта поле owner
        if hasattr(obj, "owner"):
            return obj.owner == request.user
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Только владелец может редактировать и удалять, читать могут все"""

    def has_object_permission(self, request, view, obj):
        # Чтение разрешено всем
        if request.method in permissions.SAFE_METHODS:
            return True
        # Изменение и удаление — только владельцу
        if hasattr(obj, "owner"):
            return obj.owner == request.user
        return False


class IsModeratorOrOwner(permissions.BasePermission):
    """
    Комбинированное разрешение:
    - Модератор может всё (кроме создания и удаления)
    - Владелец может всё со своими объектами
    """

    def has_permission(self, request, view):
        # Для списков: проверяем, авторизован ли пользователь
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Модератор может просматривать и редактировать любые объекты
        if user.groups.filter(name="moderators").exists():
            # Модератор не может удалять (это проверяем отдельно)
            if request.method == "DELETE":
                return False
            return True

        # Обычный пользователь — только свои объекты
        if hasattr(obj, "owner"):
            return obj.owner == user
        return False


class NotIsModerator(permissions.BasePermission):
    """Проверка, что пользователь НЕ является модератором"""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return not request.user.groups.filter(name="moderators").exists()
