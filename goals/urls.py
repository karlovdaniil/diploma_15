from django.urls import path

from goals.views.boards import BoardCreateView, BoardListView, BoardView
from goals.views.categories import CategoryCreateView, CategoryDetailView, CategoryListView
from goals.views.comments import GoalCommentCreateView, GoalCommentDetailView, GoalCommentListView
from goals.views.goals import GoalCreateView, GoalDetailView, GoalListView

app_name = 'goals'

urlpatterns = [
    # Boards
    path('board/create', BoardCreateView.as_view(), name='create-board'),
    path('board/list', BoardListView.as_view(), name='boards-list'),
    path('board/<int:pk>', BoardView.as_view(), name='board-details'),
    # Categories
    path('goal_category/create', CategoryCreateView.as_view(), name='create-category'),
    path('goal_category/list', CategoryListView.as_view(), name='categories-list'),
    path('goal_category/<int:pk>', CategoryDetailView.as_view(), name='categories-details'),
    # Goals
    path('goal/create', GoalCreateView.as_view(), name='create-goal'),
    path('goal/list', GoalListView.as_view(), name='goals-list'),
    path('goal/<int:pk>', GoalDetailView.as_view(), name='goal-details'),
    # Comments
    path('goal_comment/create', GoalCommentCreateView.as_view(), name='create-comment'),
    path('goal_comment/list', GoalCommentListView.as_view(), name='comments-list'),
    path('goal_comment/<int:pk>', GoalCommentDetailView.as_view(), name='comment-details'),
]
