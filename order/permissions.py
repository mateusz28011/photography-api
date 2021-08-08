from rest_framework import permissions


class IsVendorOrClient(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):

        return request.user in [obj.vendor, obj.client]


class CanEdit(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.client:
            data_set = set(request.data)
            forbidden_set = set(["album", "cost", "currency"])
            if forbidden_set.intersection(data_set) != set():
                return False
        return True
