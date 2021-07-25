from rest_framework import permissions


class IsAuthorOrHasAccess(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.author:
            return True
        for user in obj.allowed_users.all():
            if request.user == user:
                return True
        return False


class IsCreatorOrHasAccess(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.creator:
            return True
        for user in obj.allowed_users.all():
            if request.user == user:
                return True
        return False


class IsCreator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.creator
