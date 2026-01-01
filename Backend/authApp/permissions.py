from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Allow users to edit their own account.
    Other users can view but with limited data.
    """
    def has_object_permission(self, request, view, obj):
        # Write permissions are only allowed to the owner
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user


class CanManageOwnAccount(permissions.BasePermission):
    """
    Allow users to manage only their own account details.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class CanViewUserProfile(permissions.BasePermission):
    """
    Allow viewing other user profiles with restrictions.
    Users can see basic info but not sensitive data.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Owner can view full details
        if obj == request.user:
            return True
        # Staff can view all profiles
        if request.user.is_staff:
            return True
        # Regular users can view basic info only
        return request.method in permissions.SAFE_METHODS


class CanManageUserRole(permissions.BasePermission):
    """
    Only admin/staff can assign or revoke user roles.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff