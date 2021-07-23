from rest_framework import permissions
from rest_framework.exceptions import NotFound


class IsVendorOrClient(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in [obj.vendor, obj.client]
