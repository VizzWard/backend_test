from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Permiso personalizado para permitir acceso solo a usuarios con el rol 'admin'.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role and request.user.role.name == 'admin')
