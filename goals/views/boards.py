from django.db import transaction
from django.db.models import QuerySet
from rest_framework import filters, generics, permissions
from rest_framework.generics import RetrieveUpdateDestroyAPIView

from goals.models import Board, Goal
from goals.permissions import BoardPermission
from goals.serializers import BoardListSerializer, BoardSerializer


class BoardView(RetrieveUpdateDestroyAPIView):
    model = Board
    permission_classes = [permissions.IsAuthenticated, BoardPermission]
    serializer_class = BoardSerializer

    def get_queryset(self):
        return Board.objects.filter(participants__user=self.request.user, is_deleted=False)

    def perform_destroy(self, instance: Board):
        with transaction.atomic():
            instance.is_deleted = True
            instance.save()
            instance.categories.update(is_deleted=True)
            Goal.objects.filter(category__board=instance).update(status=Goal.Status.archived)
        return instance


class BoardListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BoardListSerializer
    filter_backends = [filters.OrderingFilter]
    ordering = ['title']

    def get_queryset(self) -> QuerySet[Board]:
        return Board.objects.filter(participants__user=self.request.user).exclude(is_deleted=True)
