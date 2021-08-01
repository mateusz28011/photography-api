from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import Profile

from .serializers import ProfileNestedSerializer, ProfileSerializer


class ProfileViewSet(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    retrieve_serializer_class = ProfileNestedSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "retrieve":
            if hasattr(self, "retrieve_serializer_class"):
                return self.retrieve_serializer_class
        return self.serializer_class

    def create(self, request, *args, **kwargs):
        if hasattr(request.user, "profile") == True:
            raise PermissionDenied({"detail": "User already has profile."})

        request.data["owner"] = request.user.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if "avatar" in request.data:
            instance.avatar.delete()
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
