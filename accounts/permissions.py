from rest_framework import permissions, generics
from rest_framework.exceptions import PermissionDenied
from accounts.models import Account, Transaction


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of accounts and transactions to access them.
    Admin users (is_staff=True) can access all data.
    """

    def has_permission(self, request, view):
        if request.user.is_staff:
            return True

        if request.method == 'GET' and isinstance(view, generics.ListAPIView):
            return True

        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        if isinstance(obj, Account):
            if obj.user != request.user:
                raise PermissionDenied("You do not have permission to access this account.")
            return True

        if isinstance(obj, Transaction):
            if obj.account.user != request.user:
                raise PermissionDenied("You do not have permission to access this transaction.")
            return True

        return False
