from django.contrib import admin

from goals.models import Goal, GoalCategory


@admin.register(GoalCategory)
class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created', 'updated')
    search_fields = ('title', 'user')


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'category', 'due_date', 'user', 'status', 'priority')
    search_fields = ('title', 'category', 'due_date', 'user', 'status', 'priority')
