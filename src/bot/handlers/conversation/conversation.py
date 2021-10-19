""" find a conversation module """

from loguru import logger
from telegram import ReplyKeyboardMarkup
from telegram import Update
from telegram.chat import Chat
from telegram.ext import CallbackContext
from telegram.ext import ConversationHandler
from telegram.utils import helpers
from datetime import timedelta

from ..handlers import start

from ...data import text
from ...data import start_keyboard
from ...db_functions import db_session
from ...states import States


def ask_conv_filters(update: Update, context: CallbackContext):
    """ asks user for filters for finding a conversation """

    chat_id = update.message.chat.id

    user_tags = db_session.get_user_tags(chat_id)
    if len(user_tags) > 0:
        return create_conv_request(update, context)

    status_list = db_session.get_tag_statuses()
    context.user_data["status_list"] = status_list
    print(status_list)

    reply_keyboard = [
        [text["skip"]],
        [text["cancel"]]
    ]
    try:
        status_idx = context.user_data["status_idx"]
    except KeyError:
        status_idx = 0
    print(status_idx)
    try:
        status = status_list[status_idx][0]
    except IndexError:
        context.user_data.pop("status_idx")
        status = status_list[status_idx][0]

    print(status)
    context.user_data["status_idx"] = status_idx+1
    tag_list = db_session.get_tags_by_status(status)
    for tag in tag_list:
        tag_name = tag.name
        reply_keyboard.append([tag_name])


    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, selective=True)

    if status == "None":
        status = "сферы"
    context.bot.send_message(
        chat_id=chat_id,
        text=f"Выберите {status}, которые лучше всего вам подходят:",
        reply_markup=markup
    )

    return States.ADD_USER_TAG

def add_user_tag(update: Update, context: CallbackContext):
    """ pass """

    chat_id = update.message.chat.id
    mssg = update.message.text

    status_list = context.user_data["status_list"]
    status_idx = context.user_data["status_idx"]

    try:
        tag_id = db_session.get_tag_by_name(mssg).id
    except AttributeError:
        return ask_conv_filters(update, context)
    
    try:
        user_tag_list = context.user_data["user_tag_list"]
        user_tag_list.append(tag_id)
    except KeyError:
        user_tag_list = []
        user_tag_list.append(tag_id)
        context.user_data["user_tag_list"] = user_tag_list
    print(user_tag_list)
    
    if status_idx == (len(status_list)- 1):
        context.user_data.pop("status_list")
        context.user_data.pop("user_tag_list")
        context.user_data.pop("status_idx")
        for user_tag in user_tag_list:
            db_session.add_user_tag(chat_id, user_tag)
        return create_conv_request(update, context)
    
    return ask_conv_filters(update, context)


def create_conv_request(update: Update, context: CallbackContext):
    """ pass """

    chat_id = update.message.chat.id

    conv_request = db_session.get_conv_request_active_by_user_id(chat_id)
    if conv_request:
        context.bot.send_message(
            chat_id=chat_id,
            text="У Вас уже есть активный запрос на разговор, мы Вас оповестим, когда найдем кого-то!",
        )
        return start(update, context)

    context.bot.send_message(
        chat_id=chat_id,
        text="Thanks, we will let you know when we find somebody!",
    )

    conv_request = db_session.create_conv_request(chat_id)
    conv_request = db_session.get_conv_request_active_by_user_id(chat_id)

    find_conversation(conv_request, context)

    # context.user_data["feedback_chat_id"] = chat_id

    return start(update, context)


def find_conversation(conv_request, context):

    user_tags = conv_request.tags
    user_tags_sorted = sorted(user_tags)
    print(user_tags)
    potential_users = db_session.get_open_users()
    for user in potential_users:

        if user.id != conv_request.user_id:
            user_two_tags = db_session.get_user_tags_by_user_id(user.id)
            user_two_tags_names = []
            for user_two_tag in user_two_tags:
                tag_name = db_session.get_tag(user_two_tag.tag_id).name
                user_two_tags_names.append(tag_name)
            user_two_tags_sorted = sorted(user_two_tags_names)

            if user_tags_sorted == user_two_tags_sorted:
                user_found(conv_request, user, user_tags, context)
                break

    
def user_found(conv_request, user_found, user_tags, context):

    db_session.update_conv_request(conv_request, user_found, user_tags)

    user_one_id = conv_request.user_id
    user_one = db_session.get_user_data_by_id(user_one_id)
    user_two = db_session.get_user_data_by_id(user_found.id)
    db_session.add_contacts(user_one.id, user_two.id)
    db_session.add_contacts(user_two.id, user_one.id)
    context.bot.send_message(
            chat_id=user_one.chat_id,
            text=f"Мы нашли вам партнера! Встречайте @{user_two.username}",
        )


