import inspect
import os

from accounts.models import User
from core.settings import BASE_DIR
from django_sendfile import sendfile
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.reverse import reverse

from album.permissions import (
    IsAuthor,
    IsAuthorOrHasAccess,
    IsCreator,
    IsCreatorOrHasAccess,
)

from .models import Album, Image
from .serializers import AlbumSerializer, ImageUploadSerializer


def get_image_path(instance):
    image = instance.image
    path = os.path.join(image.storage.base_url, image.name)
    path = BASE_DIR.__str__() + path
    return path


class AlbumViewset(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer

    def get_permissions(self):
        if self.action == "retrieve":
            permission_classes = [IsCreatorOrHasAccess]
        elif self.action == "add_image":
            permission_classes = [IsCreator]
        return [permission() for permission in permission_classes]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = AlbumSerializer(instance, context={"request": request})
        return Response(serializer.data)


class AllowedUsersViewSet(viewsets.GenericViewSet):
    queryset = Album.objects.all()
    permission_classes = [IsCreator]

    def validate(self, user, album, request):
        if user == album.creator:
            raise ValidationError({"detail": "Can not add/remove user which is album creator."})

        isFound = False
        for user_with_access in album.allowed_users.all():
            if user == user_with_access:
                if request.method == "PUT":
                    raise ValidationError({"detail": "The specified user already has access."})
                if request.method == "DELETE":
                    isFound = True

        if request.method == "DELETE" and isFound == False:
            raise ValidationError({"detail": "The specified user has no access."})

    def update(self, request, *args, **kwargs):
        album, user = self.get_object()

        self.validate(user, album, request)

        album.allowed_users.add(user)
        album.save()

        return Response({"detail": f"The user {user.email} has been granted access."})

    def destroy(self, request, pk, *args, **kwargs):
        album, user = self.get_object()

        self.validate(user, album, request)

        album.allowed_users.remove(user)
        album.save()

        return Response({"detail": f"The user {user.email} lost access."})

    def get_object(
        self,
    ):
        queryset = self.filter_queryset(self.get_queryset())
        try:
            album = queryset.get(pk=self.kwargs["album_pk"])
        except:
            raise NotFound({"album_pk": "No album matches the given album number."})
        self.check_object_permissions(self.request, album)

        try:
            user = User.objects.get(pk=self.kwargs["pk"])
        except:
            raise NotFound({"pk": "No user matches the given user id."})

        return album, user


class ImageViewset(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    queryset = Image.objects.all()
    serializer_class = ImageUploadSerializer

    def get_permissions(self):
        if self.action == "delete":
            permission_classes = [IsAuthor]
        else:
            permission_classes = [IsAuthorOrHasAccess]
        return [permission() for permission in permission_classes]

    def create(self, request, album_pk, *args, **kwargs):
        serializer = ImageUploadSerializer(data=request.data)

        try:
            album = Album.objects.get(pk=album_pk)
        except:
            raise NotFound({"album_pk": "No album matches the given album number."})

        serializer.context["album"] = album
        serializer.is_valid(raise_exception=True)

        is_allowed = IsCreator().has_object_permission(request, self, album)
        if is_allowed == False:
            raise PermissionDenied()

        image = serializer.save()

        image_url = reverse("album-images-detail", args=[album.id, image.id], request=request)
        return Response({"image": image_url}, status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        path = get_image_path(instance)
        return sendfile(request, path)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.image.delete()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
