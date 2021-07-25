import os

from accounts.models import User
from core.settings import BASE_DIR
from django_sendfile import sendfile
from rest_framework import mixins, permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from album.permissions import IsAuthorOrHasAccess, IsCreator, IsCreatorOrHasAccess

from .models import Album, Image
from .serializers import AlbumSerializer, ImageSerializer


class AlbumViewset(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    permission_classes = [IsCreatorOrHasAccess]

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


class ImageViewset(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [IsAuthorOrHasAccess]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        image = instance.image
        path = os.path.join(image.storage.base_url, image.name)
        path = BASE_DIR.__str__() + path
        return sendfile(request, path)
