""" helper functions for registration process """
from datetime import datetime
from datetime import timedelta
from enum import Enum
from functools import wraps
from os import getenv
from typing import Literal
from typing import Tuple
from typing import Union

from telegram import ReplyKeyboardMarkup
from telegram import Update
from telegram.error import BadRequest
from telegram.error import Unauthorized
from telegram.ext import CallbackContext

from ...db_functions import db_session
from ...data import text
from ...states import States
# from ...utils import cached_data
# from .account import profile
from .users_dict import users


def clean_users(context):
    """
    notify users in registration process that they need
    to finish it if they stopped for more then 15 minutes
    after 2 hours deletes from chache
    """

    if users:
        chat_id_list = list(users.keys())
        time_now = datetime.now()
        for chat_id in chat_id_list:
            users_to_be_killed = []
            time_diff = time_now - users[chat_id]["last_action_time"]
            if time_diff > timedelta(minutes=15):
                if time_diff < timedelta(hours=2):
                    context.bot.send_message(
                        chat_id=chat_id, text=text["finish_registration_pls"]
                    )
                else:
                    users_to_be_killed.append(chat_id)
        for chat_id in users_to_be_killed:
            try:
                context.bot.send_message(
                    chat_id=chat_id, text=text["restart_registration"]
                )
            except (Unauthorized, BadRequest) as error:
                context.bot.send_message(
                    chat_id="@" + getenv("LOG_CHANNEL", ""),
                    text=f"Unable to notify {chat_id} to end registration becouse of: {error}",
                )
            users.pop(chat_id, None)


def restrict_registration_time(func):
    """ send to the start of registration in case timed out and removed from users list """

    @wraps(func)
    def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
        chat_id = update.message.chat.id
        if chat_id not in users:
            context.bot.send_message(chat_id=chat_id, text=text["restart_registration"])
            return States.MENU
        return func(update, context, *args, **kwargs)

    return wrapped


class Direction(Enum):
    """ battons layout type """

    VERTICAL: str = "vertical"
    HORIZONTAL: str = "horizontal"


def generate_keyboard(
    options: Union[dict, list] = None,
    direction: Literal[Direction.VERTICAL, Direction.HORIZONTAL] = Direction.VERTICAL,
) -> ReplyKeyboardMarkup:
    """Generaty keyboard markup for registration options

    Args:
        options (dict): button options
        direction (Union[Direction.VERTICAL, Direction.HORIZONTAL]): one of possible directions

    Returns:
        ReplyKeyboardMarkup: markup
    """
    reply_keyboard = [[text["back"]]]

    if options:
        buttons = options.keys() if isinstance(options, dict) else options

        if direction == Direction.VERTICAL:
            reply_keyboard += [[i] for i in buttons]
        elif direction == Direction.HORIZONTAL:
            reply_keyboard += [list(buttons)]

    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, selective=True)
    return markup


def save_user(update: Update, context: CallbackContext):
    """ save user_data in db return profile to user or preced to timer if group """

    # print(users)
    chat_id = update.message.chat.id

    db_session.add_user_data(
        chat=update.message.chat
    )

    del users[chat_id]

    # return profile(update, context)


