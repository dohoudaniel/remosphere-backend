from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    SAFE methods (GET, HEAD, OPTIONS) → allow all authenticated users.
    Modifying methods (POST, PUT, PATCH, DELETE) → only admins.
    """

    def has_permission(self, request, view):
        # Allow read-only access for any authenticated user
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated  # True

        # For write operations — user must be admin
        return request.user.is_authenticated and request.user.is_admin
