from rest_framework import permissions


class IsAdminUserOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return bool(
            request.method in permissions.SAFE_METHODS or
            request.user and
            request.user.is_staff
        )


class IsInstanceOwnerOrReadonly(permissions.BasePermission):
    message = 'Only user created comment can delete/change it'

    def has_object_permission(self, request, view, obj):
        if request.method == 'POST':
            return request.user.is_authenticated
        return bool(request.method in permissions.SAFE_METHODS or
                    request.user.is_authenticated and
                    obj.user == request.user)
