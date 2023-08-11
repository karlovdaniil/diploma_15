from rest_framework import serializers
from rest_framework.exceptions import NotFound, PermissionDenied

from core.serializers import ProfileSerializer
from goals.models import Goal, GoalCategory, GoalComment


class GoalCategorySerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'is_deleted')


class GoalCategoryWithUserSerializer(GoalCategorySerializer):
    user = ProfileSerializer(read_only=True)


class GoalSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')

    def validate_category(self, value: GoalCategory) -> GoalCategory:
        if value.is_deleted:
            raise NotFound('Category not exists')
        if self.context['request'].user != value.user:
            raise PermissionDenied
        return value


class GoalWithUserSerializer(GoalSerializer):
    user = ProfileSerializer(read_only=True)


class GoalCommentSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')

    def validate_goal(self, value: Goal) -> Goal:
        if value.status == Goal.Status.archived:
            raise NotFound('Goal not exists')
        if self.context['request'].user != value.user:
            raise PermissionDenied
        return value


class GoalCommentWithUserSerializer(GoalCommentSerializer):
    user = ProfileSerializer(read_only=True)
    goals = serializers.PrimaryKeyRelatedField(read_only=True)
