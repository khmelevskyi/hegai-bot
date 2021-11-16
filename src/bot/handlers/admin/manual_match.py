""" basic single functions and admin menu """
import re

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram import Update
from telegram.ext import CallbackContext
from loguru import logger

from .admin import admin
from ...db_functions import db_session
from ...data import text
from ...states import States


def ask_users_to_match(update: Update, context: CallbackContext):
    """ asks user to enter either telegram usernames or notion links of users to match """
    chat_id = update.message.chat.id

    reply_keyboard = [
        [text["back"]],
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, selective=True)

    context.bot.send_message(
        chat_id=chat_id,
        text="Введите телеграм юзернеймы пользователей или ссылки на их notion страницы по примеру:\n\n"
        "Пример:\n@user1 и @user2\nили\n"
        "https://www.notion.so/phegai/a64b82078a7d4d9babecb16647d5e95a и https://www.notion.so/phegai/a64b82078a7d4d9babecb16647d5e95a",
        reply_markup=markup,
    )

    return States.MANUAL_MATCH


def manual_match(update: Update, context: CallbackContext):
    """ asks user to enter either telegram usernames or notion links of users to match """
    chat_id = update.message.chat.id
    answer = update.message.text

    users = []
    if "@" in answer:
        usernames = re.findall(r"(\B\@\w+)", answer)
        for username in usernames:
            user = db_session.get_user_data_by_username(username.replace("@", ""))
            users.append(user)

    elif "notion" in answer:
        links = re.findall(r"(phegai/\w+)", answer)
        for link in links:
            user_found_notion_id = link.replace("phegai/", "")
            user_found_notion_id = (
                user_found_notion_id[:8]
                + "-"
                + user_found_notion_id[8:12]
                + "-"
                + user_found_notion_id[12:16]
                + "-"
                + user_found_notion_id[16:20]
                + "-"
                + user_found_notion_id[20:32]
            )
            user = db_session.get_user_data_by_notion_id(user_found_notion_id)
            users.append(user)

    try:
        context.bot.send_message(
            chat_id=chat_id,
            # chat_id=users[0].chat_id,
            text=f"Вам нашли собеседника: @{users[1].username}",
            reply_markup=ReplyKeyboardRemove(),
        )
        context.bot.send_message(
            chat_id=chat_id,
            # chat_id=users[1].chat_id,
            text=f"Вам нашли собеседника: @{users[0].username}",
            reply_markup=ReplyKeyboardRemove(),
        )

        db_session.add_contacts(users[0].id, users[1].id)
        db_session.add_contacts(users[1].id, users[0].id)
    except (IndexError, AttributeError) as error:
        logger.error(error)
        context.bot.send_message(
            chat_id=chat_id,
            text="Неправильный ввод данных или таких пользователей не существует!",
            reply_markup=ReplyKeyboardRemove(),
        )

    return admin(update, context)
