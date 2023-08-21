from typing import Any, Callable

from django.core.management import BaseCommand
from pydantic.main import BaseModel

from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.schemas import Message
from goals.models import Goal, GoalCategory
from todolist.settings import HOST


class FSM(BaseModel):
    next_handler: Callable
    data: dict[str, Any] = {}


users: dict[int, FSM] = {}


class Command(BaseCommand):
    tg_client = TgClient()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient()

    def handle(self, *args, **options):
        offset = 0

        while True:
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                self.handle_message(item.message)

    def handle_message(self, msg: Message) -> None:
        tg_user, _ = TgUser.objects.get_or_create(chat_id=msg.chat.id, defaults={'username': msg.chat.username})
        if not tg_user.is_verified:
            tg_user.update_verification_code()
            verification_code = tg_user.verification_code
            text = f'Enter the verification code on the website: {verification_code}'
            self.tg_client.send_message(chat_id=msg.chat.id, text=text)
        else:
            self.handle_auth_user(tg_user, msg)

    def handle_auth_user(self, tg_user: TgUser, msg: Message) -> None:
        """Processing messages from authorized users"""
        if msg.text == '/goals':
            goals_str = self.get_goals(tg_user=tg_user)
            self.tg_client.send_message(msg.chat.id, goals_str)
        elif msg.text == '/create':
            self.send_categories(tg_user=tg_user)
        elif msg.text == '/cancel':
            users.pop(tg_user.chat_id, None)
            self.tg_client.send_message(tg_user.chat_id, 'Cancelled successfully')
        elif msg.chat.id in users:
            users[tg_user.chat_id].next_handler(tg_user, msg)
        else:
            self.tg_client.send_message(tg_user.chat_id, 'Unknown command')

    def send_categories(self, tg_user: TgUser):
        """Sending a list of categories to the user to create a goal"""
        categories = GoalCategory.objects.filter(user=tg_user.user, is_deleted=False)
        categories_dict: dict = {category.title: category for category in categories}
        categories_list = list(categories_dict.keys())
        if categories_list:
            categories_str = '\n'.join(categories_list)
            self.tg_client.send_message(tg_user.chat_id, f'Select a category to create a goal: {categories_str}')
            users[tg_user.chat_id] = FSM(next_handler=self.handle_get_category)
            users[tg_user.chat_id].data.update({'categories': categories_dict})
        else:
            self.tg_client.send_message(
                tg_user.chat_id, 'You do not have a single category, it is impossible to create a goal'
            )

    def handle_get_category(self, tg_user: TgUser, msg):
        """Getting a category to create a goal from a user"""
        categories_list = list(users[tg_user.chat_id].data['categories'].keys())
        if msg.text:
            if msg.text in categories_list:
                self.tg_client.send_message(tg_user.chat_id, 'Category selected')
                self.tg_client.send_message(tg_user.chat_id, f'Name of your goal?')
                users[msg.chat.id].data.update({'category': msg.text})
                users[msg.chat.id].next_handler = self.handle_create_goal
            else:
                self.tg_client.send_message(tg_user.chat_id, 'You do not have such a category')
                users.pop(tg_user.chat_id, None)
                self.send_categories(tg_user=tg_user)

    def handle_create_goal(self, tg_user: TgUser, msg):
        """Creating a new goal and sending a link to it to the user"""
        if msg.text:
            category_str = users[tg_user.chat_id].data.get('category')
            category = users[tg_user.chat_id].data['categories'][category_str]
            goal = Goal.objects.create(category=category, title=msg.text, user=tg_user.user)
            self.tg_client.send_message(
                msg.chat.id,
                f'The goal was created at http://{HOST}/boards/{category.board.pk}'
                f'/categories/{category.id}/goals?goal={goal.pk}',
            )
            users.pop(msg.message_from.id, None)

    def get_goals(self, tg_user: TgUser) -> str:
        goals = Goal.objects.filter(user=tg_user.user, category__is_deleted=False).exclude(status=Goal.Status.archived)
        goals_list: list[str] = [f'Goal: {goal.title}, deadline {goal.due_date}' for goal in goals]

        if goals_list:
            goals_str = '\n'.join(goals_list)
        else:
            goals_str = 'No targets found'

        return goals_str
