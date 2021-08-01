from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from album.models import Album


class IsAuthorOrHasAccess(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.album.is_public == True:
            return True
        if request.user == obj.author:
            return True
        for user in obj.album.allowed_users.all():
            if request.user == user:
                return True
        return False


class IsAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.author


class CanCreate(permissions.BasePermission):
    def has_permission(self, request, view):
        print("dupa")
        if "parent_album" in request.data:
            parent_album = Album.objects.get(pk=request.data["parent_album"])
            print(True)
            if parent_album.creator != request.user:
                raise PermissionDenied()
        return request.user.is_vendor


class IsCreatorOrHasAccess(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.album.is_public == True:
            return True
        if request.user == obj.creator:
            return True
        for user in obj.allowed_users.all():
            if request.user == user:
                return True
        return False


class IsCreator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):

        return request.user == obj.creator
