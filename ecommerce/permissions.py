# ecommerce/permissions.py

from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsStaffOrReadOnly(BasePermission):
    """
    Allows read-only access to anyone,
    but write access only to staff users.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff
