from rest_framework import mixins, permissions, serializers, status, viewsets
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response

from .models import Note, Order
from .permissions import IsVendorOrClient
from .serializers import NoteSerializer, OrderNestedSerializer, OrderSerializer


class OrderViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    retrieve_list_serializer_class = OrderNestedSerializer
    permission_classes = [IsVendorOrClient]

    def get_serializer_class(self):
        if self.action in ["retrieve", "list"]:
            if hasattr(self, "retrieve_list_serializer_class"):
                return self.retrieve_list_serializer_class
        return self.serializer_class


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
        note = serializer.save(user=request.user)

        order.notes.add(note)
        order.save()

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
