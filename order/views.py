from album.models import Album
from core.utils import SwaggerOrderingFilter, SwaggerSearchFilter
from django.db.models import Q
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Note, Order
from .permissions import CanEdit, IsVendorOrClient
from .serializers import (
    NoteSerializer,
    OrderCreateSerializer,
    OrderListSerializer,
    OrderNestedSerializer,
    OrderUpdateSerializer,
)


class OrderFilter(filters.FilterSet):
    is_client = filters.BooleanFilter(field_name="client", method="filter_is_client")
    is_vendor = filters.BooleanFilter(field_name="vendor", method="filter_is_vendor")

    def filter_is_client(self, queryset, name, value):
        lookup = "__".join([name, "exact"])
        return queryset.filter(**{lookup: self.request.user.id})

    def filter_is_vendor(self, queryset, name, value):
        lookup = "__".join([name, "exact"])
        return queryset.filter(**{lookup: self.request.user.id})

    class Meta:
        model = Order
        fields = ["status"]


class OrderViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderListSerializer
    filter_backends = [DjangoFilterBackend, SwaggerOrderingFilter, SwaggerSearchFilter]
    filterset_class = OrderFilter
    # filterset_fields = ["client", "vendor", "status"]
    search_fields = ["vendor__profile__name", "client__first_name", "client__last_name", "client__email"]
    ordering_fields = ["created", "status", "cost"]
    ordering = ["-created"]

    def get_queryset(self):
        return self.queryset.filter(Q(client=self.request.user.id) | Q(vendor=self.request.user.id))

    def get_serializer_class(self):
        if self.action == "partial_update":
            return OrderUpdateSerializer
        elif self.action == "create":
            return OrderCreateSerializer
        elif self.action == "retrieve":
            return OrderNestedSerializer
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

    @swagger_auto_schema(
        operation_description="""
        **Available statuses:**
        
        The created orders have default status of 2.

                0 - Canceled
                1 - Rejected
                2 - Waiting for acceptance
                3 - Accepted
                4 - Waiting for payment
                5 - Payment received
                6 - Finished
        ### Permissions
        If order status is 0, 1 or 6 it cannot be changed.
        * ### Client
            Can only update status.
            Can only update status when it is 2 and can only be set to 0.

        * ### Vendor
            Upating album automatically adds client to allowed users and makes it private.
            Available update for specific status:
            * 2 -> 1 or 3
            * 3 -> 0, 4 or 6
                * If setting to 4, cost cannot be null.
            * 4 -> 0, 5, 6
            * 5 -> 0 or 6
        """
    )
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        if "album" in request.data and request.data["album"] == None:
            album = instance.album
            album.allowed_users.remove(instance.client)
            album.save()

        instance = serializer.save()

        if "album" in request.data and request.data["album"] != None:
            album = instance.album
            album.allowed_users.add(instance.client)
            album.is_public = False
            album.save()

        return Response(serializer.data)


class NoteViewSet(viewsets.GenericViewSet):
    queryset = Order.objects.all()
    serializer_class = NoteSerializer
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

    #     notes = obj.note_set.all()
    #     return NoteSerializer(notes, many=True).data
    def list(self, request, *args, **kwargs):
        order = self.get_object()
        queryset = order.note_set.all().order_by("-created")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(operation_description="Add note to specified order.")
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = self.get_object()
        serializer.save(user=request.user, order=order)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(operation_description="Edit note in specified order.\n**\{id\}** is note's id.")
    def partial_update(self, request, pk, *args, **kwargs):
        # To check order permissions.
        self.get_object()

        try:
            note = Note.objects.get(pk=pk)
        except:
            raise NotFound({"pk": "No note matches the given note number."})

        if note.user != request.user:
            raise PermissionDenied()

        serializer = self.get_serializer(note, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
