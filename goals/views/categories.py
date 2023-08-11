from django.db import transaction
from rest_framework import filters, generics, permissions

from goals.models import Goal, GoalCategory
from goals.permissions import GoalCategoryPermission
from goals.serializers import GoalCategorySerializer, GoalCategoryWithUserSerializer


class CategoryCreateView(generics.CreateAPIView):
    serializer_class = GoalCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class CategoryListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategoryWithUserSerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['title', 'created']
    ordering = ['title']
    search_fields = ['title']

    def get_queryset(self):
        return GoalCategory.objects.select_related('user').filter(user=self.request.user).exclude(is_deleted=True)


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GoalCategoryWithUserSerializer
    permission_classes = [GoalCategoryPermission]

    def get_queryset(self):
        return GoalCategory.objects.select_related('user').exclude(is_deleted=True)

    def perform_destroy(self, instance: GoalCategory):
        with transaction.atomic():
            instance.is_deleted = True
            instance.save()
            instance.goal_set.update(status=Goal.Status.archived)
