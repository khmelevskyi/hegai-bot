""" basic single functions and admin menu """
from telegram import ParseMode
from telegram import ReplyKeyboardMarkup
from telegram import Update
from telegram.ext import CallbackContext

from ...hegai_db import Permission
from ...db_functions import db_session
# from ..admins import ADMINS
from ...data import text
from ...states import States


def admin_keyboard_markup() -> ReplyKeyboardMarkup:
    """ returns admin keyboard layout """

    admin_keyboard = [
        [text["see_uni"], text["change_uni"]],
        [text["add_room"], text["tag_map"]],
        [text["back"]],
    ]
    markup = ReplyKeyboardMarkup(keyboard=admin_keyboard, resize_keyboard=True)
    return markup


def admin(update: Update, context: CallbackContext):
    """ welcomes admin """
    chat_id = update.message.chat.id
    # university_id = db_session.get_user_data(chat_id=chat_id)[0]
    university = "uni" # cached_data.list_universities()[university_id][0]
    context.bot.send_message(
        chat_id=chat_id,
        text=text["hi_admin"].format(university, "admin"), # ADMINS[chat_id][0]
        reply_markup=admin_keyboard_markup(),
        parse_mode=ParseMode.HTML,
    )
    return States.ADMIN_MENU


def drop_user(update: Update, context: CallbackContext):
    """ drop user from all tables in db """

    msg = update.message.text
    split_msg = msg.split(" ")
    if len(split_msg) == 1:
        context.bot.send_message(
            chat_id=update.message.chat.id,
            text="id not provided, use it like:\n\n/drop 1488228",
        )
    else:
        chat_id = int(split_msg[-1])
        error, db_msg = db_session.drop_user_cascade(chat_id)
        if not error:
            context.bot.send_message(
                chat_id=chat_id,
                text=text["user_deleted"],
            )
        full_msg = f"Error: {error}\n\n{db_msg}"
        context.bot.send_message(
            chat_id=update.message.chat.id,
            text=full_msg,
        )


def set_user(update: Update, context: CallbackContext):
    """ set uni_id and user data to admin account """

    msg = update.message.text
    split_msg = msg.split(" ")
    if len(split_msg) == 1:
        context.bot.send_message(
            chat_id=update.message.chat.id,
            text="id not provided, use it like:\n\n/set 1488228",
        )
    else:
        admin_id = update.message.chat.id
        chat_id = int(split_msg[-1])
        error, db_msg = db_session.set_user(admin_id, chat_id)
        full_msg = f"Error: {error}\n\n{db_msg}"
        context.bot.send_message(
            chat_id=update.message.chat.id,
            text=full_msg,
        )

