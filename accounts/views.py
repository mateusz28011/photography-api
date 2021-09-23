from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from core.utils import SwaggerOrderingFilter, SwaggerSearchFilter
from dj_rest_auth.registration.views import SocialLoginView
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from accounts.models import Profile, User
from accounts.permissions import IsOwner

from .paginations import UserListPagination
from .serializers import (
    ProfileListSerializer,
    ProfileSerializer,
    UserBasicInfoSerializer,
)


class UserViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.get_queryset().order_by("email")
    serializer_class = UserBasicInfoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SwaggerSearchFilter]
    search_fields = ["email", "first_name", "last_name"]
    pagination_class = UserListPagination

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        queryset = queryset.exclude(id=self.request.user.id)
        return queryset


class ProfileViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SwaggerOrderingFilter, SwaggerSearchFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created"]
    ordering = ["name"]

    def get_serializer_class(self):
        if self.action == "list":
            return ProfileListSerializer
        return self.serializer_class

    def get_permissions(self):
        if self.action == "retrieve" or self.action == "list":
            permission_classes = [AllowAny]
        elif self.action == "create":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated & IsOwner]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="""
        By creating a profile, the user becomes a vendor.
        Avatar is restricted to 500x500 px.
        If it is not set, it is set to the default.
        """
    )
    def create(self, request, *args, **kwargs):
        if hasattr(request.user, "profile") == True:
            raise PermissionDenied({"detail": "User already has profile."})

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data["owner"] = request.user
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        if "avatar" in request.data:
            if instance.avatar != "default/avatar.png":
                instance.avatar.delete()
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter
