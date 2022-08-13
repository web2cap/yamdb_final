from rest_framework import permissions


class PostOnlyNoCreate(permissions.BasePermission):
    """Разрешает только метод POST. Запрещает действие метода POST create."""

    def has_permission(self, request, view):
        accept_methods = ("token", "signup")
        return request.method == "POST" and view.action in accept_methods


class IsRoleAdmin(permissions.BasePermission):
    """Разрешает доступ пользователям с ролью admin и суперпользователям."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_superuser
        )


class MeOrAdmin(permissions.BasePermission):
    """Разрешает запрос на /me/. Полный доступ админам."""

    def has_permission(self, request, view):
        path_end = request.path_info.split("/")[-2]
        return request.user.is_authenticated and (
            request.user.is_admin
            or request.user.is_superuser
            or path_end == "me"
        )


class RoleAdminrOrReadOnly(permissions.BasePermission):
    """Доступ на чтение всем. Полный доступ админу и суперпользователю."""

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated
            and (request.user.is_admin or request.user.is_superuser)
        )


class AuthorAdminModeratorOrReadOnly(permissions.BasePermission):
    """Permissions for Admin, Author, Moderator."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS) or (
            obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )
