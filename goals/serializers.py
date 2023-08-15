from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from core.models import User
from core.serializers import ProfileSerializer
from goals.models import Board, BoardParticipant, Goal, GoalCategory, GoalComment


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        read_only_fields = ('id', 'created', 'updated', 'is_deleted')
        fields = '__all__'


class BoardParticipantSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(required=True, choices=BoardParticipant.editable_role)
    user = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())

    def validated_user(self, user: User) -> User:
        if self.context['request'].user == user:
            raise ValidationError('Failed to change your role')
        return user

    class Meta:
        model = BoardParticipant
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'board')


class BoardWithParticipantsSerializer(BoardSerializer):
    participants = BoardParticipantSerializer(many=True)

    def update(self, instance: Board, validated_data: dict) -> Board:
        request_user: User = self.context['request'].user

        with transaction.atomic():
            BoardParticipant.objects.filter(board=instance).exclude(user=request_user).delete()
            BoardParticipant.objects.bulk_create(
                [
                    BoardParticipant(user=participant['user'], role=participant['role'], board=instance)
                    for participant in validated_data.get('participant', [])
                ],
                ignore_conflicts=True,
            )

            if title := validated_data.get('title'):
                instance.title = title

            instance.save()

        return instance


class GoalCategorySerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_board(self, board: Board) -> Board:
        if board.is_deleted:
            raise ValidationError('Board not exists')

        if not BoardParticipant.objects.filter(
            board_id=board.id,
            user_id=self.context['request'].user.id,
            role__in=[BoardParticipant.Role.writer, BoardParticipant.Role.owner],
        ).exists():
            raise PermissionDenied

        return board

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

    def validate_category(self, category: GoalCategory) -> GoalCategory:
        if category.is_deleted:
            raise ValidationError('Category not exists')

        if not BoardParticipant.objects.filter(
            board_id=category.board_id,
            user_id=self.context['request'].user.id,
            role__in=[BoardParticipant.Role.writer, BoardParticipant.Role.owner],
        ).exists():
            raise PermissionDenied

        return category


class GoalWithUserSerializer(GoalSerializer):
    user = ProfileSerializer(read_only=True)


class GoalCommentSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')

    def validate_goal(self, goal: Goal) -> Goal:
        if goal.status == Goal.Status.archived:
            raise ValidationError('Goal not exists')

        if not BoardParticipant.objects.filter(
            board_id=goal.category.board_id,
            user_id=self.context['request'].user.id,
            role__in=[BoardParticipant.Role.writer, BoardParticipant.Role.owner],
        ).exists():
            raise PermissionDenied

        return goal


class GoalCommentWithUserSerializer(GoalCommentSerializer):
    user = ProfileSerializer(read_only=True)
    goals = serializers.PrimaryKeyRelatedField(read_only=True)
