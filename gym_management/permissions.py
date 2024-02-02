from rest_framework.permissions import BasePermission

class IsTrainerUser(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "Coach")