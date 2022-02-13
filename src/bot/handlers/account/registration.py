""" regestration start simular both for student and teacher """
import json
import os
from datetime import datetime

from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import Update
from telegram.ext import CallbackContext

from ...data import text
from ...db_functions import db_session
from ...states import States
from .account import profile
from .users_dict import users
from .utils import restrict_registration_time

# from ...utils import cached_data
# from .utils import save_user


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
            chat_id=chat_id,
            text="Кажется у вас нет юзернейма, введите тот, который указан у Вас в Ноушне сообщества:",
            reply_markup=ReplyKeyboardRemove(),
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
            username = username.replace("@", "").lower()

    try:
        username = (
            username.lower()
        )  # in db username are lowercase, bc in notion there are links to TG
    except AttributeError:
        username = None

    try:
        notion_id = db_session.get_user_data_by_username(username).notion_id
    except AttributeError:
        context.bot.send_message(
            chat_id=chat_id,
            text="Извините, но Вы не часть сообщества. Напишите в поддержку @Hegaibot, если считаете, что произошла ошибка",
            reply_markup=ReplyKeyboardRemove(),
        )
        return None

    if username in all_usernames or username in default_list:
        if username in default_list:
            notion_id = 1
        users[chat_id]["username"] = username
        users[chat_id]["notion_id"] = notion_id
        reply_keyboard = [[text["yes"], text["no"]], [text["back"]]]

        markup = ReplyKeyboardMarkup(
            keyboard=reply_keyboard, resize_keyboard=True, selective=True
        )

        context.bot.send_message(
            chat_id=chat_id,
            text="Вы открыты к общению?",
            reply_markup=markup,
        )
        return States.ASK_CONV_OPEN
    else:
        context.bot.send_message(
            chat_id=chat_id,
            text="Извините, но Вы не часть сообщества. Напишите в поддержку @Hegaibot, если считаете, что произошла ошибка",
            reply_markup=ReplyKeyboardRemove(),
        )


@restrict_registration_time
def get_if_open_ask_max_conv_requests_week(update: Update, context: CallbackContext):
    """ saves info about if user is open to conversation and sends link to the bot-partner """

    chat_id = update.message.chat.id
    mssg = update.message.text
    boolen_val = {text["yes"]: True, text["no"]: False}

    users[chat_id]["last_action_time"] = datetime.now()

    context.user_data["is_conv_open"] = boolen_val[mssg]

    reply_keyboard = [["1", "2"], ["3", "4"], ["5", "10"]]

    markup = ReplyKeyboardMarkup(
        keyboard=reply_keyboard, resize_keyboard=True, selective=True
    )

    context.bot.send_message(
        chat_id=chat_id,
        text="Сколько максимум запросов на разговор желаете в неделю?\nВыберите вариант ниже или напишите сами(1-100):",
        reply_markup=markup,
    )

    return States.ASK_CONV_REQUEST_WEEK_MAX


@restrict_registration_time
def registration_final(update: Update, context: CallbackContext):
    """ saves info about if user is open to conversation and sends link to the bot-partner """

    chat_id = update.message.chat.id
    username = users[chat_id]["username"]
    notion_id = users[chat_id]["notion_id"]
    mssg = update.message.text

    users[chat_id]["last_action_time"] = datetime.now()

    db_session.add_user_data(
        chat=update.message.chat,
        notion_id=notion_id,
        username=username,
        conversation_open=context.user_data["is_conv_open"],
        conv_requests_week_max=int(mssg),
    )

    del users[chat_id]

    context.bot.send_message(
        chat_id=chat_id,
        text="Вы авторизованы!",
        reply_markup=ReplyKeyboardRemove(),
    )

    return profile(update, context)


# @restrict_registration_time
# def authorize_user(update: Update, context: CallbackContext):
#     """ save user data in his account in db """

#     chat_id = update.message.chat.id

#     users[chat_id]["last_action_time"] = datetime.now()

#     return save_user(update, context)
