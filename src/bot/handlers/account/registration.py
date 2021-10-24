""" regestration start simular both for student and teacher """
import os
import json
from datetime import datetime

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram import Update
from telegram.ext import CallbackContext

# from ...admins import ADMINS
from ...data import text
from ...states import States
from ...db_functions import db_session
# from ...utils import cached_data
from .users_dict import users
from .utils import restrict_registration_time
# from .utils import save_user
from .account import profile


def check_username(update: Update, context: CallbackContext):
    """ checks if user has TG username """
    chat_id = update.message.chat.id
    username = update.message.chat.username

    users[chat_id] = {
        "username": None,
        "notion_id": None,
        "last_action_time": datetime.now(),
    }

    if username:
        return check_notion_username(update, context)
    else:
        context.bot.send_message(
            chat_id=chat_id, text="Seems like u have no username, enter one:", reply_markup=ReplyKeyboardRemove()
        )
        return States.ASK_USERNAME


@restrict_registration_time
def check_notion_username(update: Update, context: CallbackContext):
    """ checks TG username with notion registry """

    default_list = json.loads(os.getenv("default_list"))

    all_usernames = db_session.get_all_usernames()

    chat_id = update.message.chat.id
    username = update.message.chat.username

    if not username:
        users[chat_id]["last_action_time"] = datetime.now()
        username = update.message.text
        if "@" in username:
            username = username.replace("@", "")

    if username in all_usernames or username in default_list:
        if username in default_list:
            notion_id = 1
        users[chat_id]["username"] = username
        users[chat_id]["notion_id"] = notion_id
        reply_keyboard = [
            [text["yes"], text["no"]],
            [text["back"]]
        ]

        markup = ReplyKeyboardMarkup(
            keyboard=reply_keyboard, resize_keyboard=True, selective=True
        )

        context.bot.send_message(
            chat_id=chat_id, text="Are you open for a conversation?", reply_markup=markup
        )
        return States.ASK_CONV_OPEN
    else:
        context.bot.send_message(
        chat_id=chat_id,
        text="Sorry, not part of the community. Write to support, if this is a mistake",
        reply_markup=ReplyKeyboardRemove()
    )


@restrict_registration_time
def registration_final(update: Update, context: CallbackContext):
    """ saves info about if user is open to conversation and sends link to the bot-partner """

    chat_id = update.message.chat.id
    username = users[chat_id]["username"]
    notion_id = users[chat_id]["notion_id"]
    mssg = update.message.text
    boolen_val = {
        text["yes"]: True,
        text["no"]: False
    }

    users[chat_id]["last_action_time"] = datetime.now()

    db_session.add_user_data(
        chat=update.message.chat,
        notion_id=notion_id,
        username=username,
        conversation_open=boolen_val[mssg]
    )

    del users[chat_id]

    context.bot.send_message(
        chat_id=chat_id,
        text="You are authorized! The link to bot-partner:",
        reply_markup=ReplyKeyboardRemove()
    )

    return profile(update, context)



# @restrict_registration_time
# def authorize_user(update: Update, context: CallbackContext):
#     """ save user data in his account in db """

#     chat_id = update.message.chat.id

#     users[chat_id]["last_action_time"] = datetime.now()

#     return save_user(update, context)
