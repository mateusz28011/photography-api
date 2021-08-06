import os

from accounts.models import User
from core.settings import BASE_DIR
from django_sendfile import sendfile
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse

from album.permissions import (
    CanCreate,
    IsAuthor,
    IsAuthorOrHasAccess,
    IsCreator,
    IsCreatorOrHasAccess,
)

from .models import Album, Image
from .serializers import (
    AlbumCreateUpdateSerializer,
    AlbumSerializer,
    ImageUpdateSerializer,
    ImageUploadSerializer,
)


class AlbumViewset(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    create_update_serializer_class = AlbumCreateUpdateSerializer

    def get_serializer_class(self):
        if self.action == "create" or self.action == "partial_update":
            if hasattr(self, "create_update_serializer_class"):
                return self.create_update_serializer_class
        return self.serializer_class

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [IsAuthenticated & CanCreate]
        elif self.action == "partial_update":
            permission_classes = [IsAuthenticated & CanCreate & IsCreator]
        elif self.action == "retrieve":
            permission_classes = [IsCreatorOrHasAccess]
        else:
            permission_classes = [IsCreator]
        return [permission() for permission in permission_classes]

    def partial_update(self, request, pk, *args, **kwargs):
        if "parent_album" in request.data:
            if request.data["parent_album"] == pk:
                raise ValidationError({"parent_album": "Cannot be itself."})

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.validated_data["creator"] = self.request.user
        serializer.save()

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
    update_serializer_class = ImageUpdateSerializer

    def get_permissions(self):
        if self.action in ["destroy", "partial_update"]:
            permission_classes = [IsAuthor]
        else:
            permission_classes = [IsAuthorOrHasAccess]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == "partial_update":
            if hasattr(self, "update_serializer_class"):
                return self.update_serializer_class
        return self.serializer_class

    def partial_update(self, request, album_pk, pk, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def create(self, request, album_pk, *args, **kwargs):
        serializer = ImageUploadSerializer(data=request.data)

        try:
            album = Album.objects.get(pk=album_pk)
        except:
            raise NotFound({"album_pk": "No album matches the given album number."})

        is_allowed = IsCreator().has_object_permission(request, self, album)
        if is_allowed == False:
            raise PermissionDenied()

        serializer.is_valid(raise_exception=True)
        serializer.validated_data["author"] = album.creator
        serializer.validated_data["album"] = album
        image = serializer.save()

        image_url = reverse("album-images-detail", args=[album.id, image.id], request=request)
        return Response({"id": image.id, "image": image_url}, status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        path = os.path.normpath(BASE_DIR.__str__() + instance.image.url)
        return sendfile(request, path)
