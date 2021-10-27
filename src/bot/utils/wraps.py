""" collection of wraps """
from functools import wraps
from typing import List
from typing import Literal

from telegram import Bot
from telegram import ReplyKeyboardRemove
from telegram import Update
from telegram.chat import Chat
from telegram.chataction import ChatAction
from telegram.ext import CallbackContext

from ..hegai_db import Permission
from ..db_functions import db_session
from ..data import text
from ..states import States
from ..utils import cached


PermissionType = Literal[
    Permission.STAT,
    Permission.PARSE,
    Permission.PUSH,
    Permission.AD,
    Permission.DROP,
    Permission.SET,
    None,
]


def restricted(permission: PermissionType):
    """ disable usage for non admin users and by permissions """

    def inner(func):
        @wraps(func)
        def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
            chat_id = update.effective_user.id
            user_id = db_session.get_user_data(chat_id).id

            if user_id not in db_session.get_admins():
                update.message.reply_text(text["forbidden"])
                return States.MENU

            if not permission:
                return func(update, context, *args, **kwargs)

            update.message.reply_text(text["role_forbidden"])
            return States.MENU

        return wrapped

    return inner


@cached  # type: ignore
def get_admin_ids(bot: Bot, chat_id: int) -> List[int]:
    """Returns a list of admin IDs for a given chat """
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]


def group_filter(func):
    """ disable usage in groups for non admin users """

    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):

        # if chat is private - no need for limitations
        if update.message.chat.type == Chat.PRIVATE:
            return func(update, context, *args, **kwargs)

        user_id = update.effective_user.id
        chat_id = update.message.chat.id

        # if chat is group - check if user is admin
        group_admin_ids = get_admin_ids(context.bot, chat_id)
        if user_id in group_admin_ids:
            return func(update, context, *args, **kwargs)

        # user is not admin - fuck him and remove his keyboard
        context.bot.send_message(
            chat_id=chat_id,
            text=text["group_warning"],
            reply_markup=ReplyKeyboardRemove(selective=True),
            reply_to_message_id=update.message.message_id,
        )
        return None

    return wrapper


def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update: Update, context: CallbackContext, *args, **kwargs):
        context.bot.send_chat_action(
            chat_id=update.effective_message.chat_id, action=ChatAction.TYPING
        )
        return func(update, context, *args, **kwargs)

    return command_func
