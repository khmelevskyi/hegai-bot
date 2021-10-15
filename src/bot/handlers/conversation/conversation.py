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

    reply_keyboard = [
        [text["cancel"]],
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, selective=True)

    context.bot.send_message(
        chat_id=chat_id,
        text="Enter filters to find a conversation for you:",
        reply_markup=markup
    )

    return States.FIND_CONVERSATION


def find_conversation(update: Update, context: CallbackContext):
    """ pass """

    chat_id = update.message.chat.id

    context.bot.send_message(
        chat_id=chat_id,
        text="Thanks, we will let you know when we find somebody!",
    )

    # context.user_data["feedback_chat_id"] = chat_id

    return start(update, context)

