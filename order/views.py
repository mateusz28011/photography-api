from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Note, Order
from .permissions import CanEdit, IsVendorOrClient
from .serializers import (
    NoteSerializer,
    OrderNestedSerializer,
    OrderSerializer,
    OrderUpdateSerializer,
)


class OrderViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    retrieve_list_serializer_class = OrderNestedSerializer
    update_serializer_class = OrderUpdateSerializer

    def get_serializer_class(self):
        if self.action in ["retrieve", "list"]:
            if hasattr(self, "retrieve_list_serializer_class"):
                return self.retrieve_list_serializer_class
        elif self.action == "partial_update":
            if hasattr(self, "update_serializer_class"):
                return self.update_serializer_class
        return self.serializer_class

    def get_permissions(self):
        if self.action == "partial_update":
            permission_classes = [IsAuthenticated & IsVendorOrClient & CanEdit]
        else:
            permission_classes = [IsAuthenticated & IsVendorOrClient]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data["client"] = request.user.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        serializer.save(client=request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        if "album" in request.data:
            album = instance.album
            album.allowed_users.add(instance.client)
            album.save()

        return Response(serializer.data)


class NoteViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsVendorOrClient]

    def get_object(
        self,
    ):
        queryset = self.filter_queryset(self.get_queryset())
        try:
            obj = queryset.get(pk=self.kwargs["order_pk"])
        except:
            raise NotFound({"order_pk": "No order matches the given order number."})
        self.check_object_permissions(self.request, obj)

        return obj

    def create(self, request, *args, **kwargs):
        serializer = NoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = self.get_object()
        serializer.save(user=request.user, order=order)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, pk, *args, **kwargs):
        # To check order permissions.
        self.get_object()

        try:
            note = Note.objects.get(pk=pk)
        except:
            raise NotFound({"pk": "No note matches the given note number."})

        if note.user != request.user:
            raise PermissionDenied()

        serializer = NoteSerializer(note, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)
