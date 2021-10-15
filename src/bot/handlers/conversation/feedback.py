""" ask for feedback module """

from loguru import logger
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram import Update
from telegram.chat import Chat
from telegram.ext import CallbackContext
from telegram.ext import ConversationHandler
from telegram.utils import helpers

from ..handlers import start

from ...data import text
from ...data import start_keyboard
from ...db_functions import db_session
from ...states import States


def ask_feedback(*args):
    """ asks for user's feedback 3 days after a conversation """

    if len(args) == 1:  # depends if it called by job_queue or updater
        context = args[0]
        chat_id = context.user_data["feedback_chat_id"]
    else:
        update, context = args[0], args[1]
        chat_id = update.message.chat.id

    reply_keyboard = [
        [text["yes"]],
        [text["no"]]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, selective=True)

    context.bot.send_message(
        chat_id=chat_id,
        text="Time for feedback!\nHave you had the conversation?",
        reply_markup=markup
    )

    return States.ASK_FEEDBACK

def ask_feedback_result(update: Update, context: CallbackContext):
    """ asks for an estimation of a conversation or its absence explanation """

    chat_id = update.message.chat.id
    mssg = update.message.text

    if mssg == text["yes"]:

        reply_keyboard = [
            ["1", "2"],
            ["3", "4"],
            ["5"]
        ]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, selective=True)

        context.bot.send_message(
            chat_id=chat_id,
            text="Nice! Estimate the conversation from 1 to 5:",
            reply_markup=markup
        )
    else:
        context.bot.send_message(
            chat_id=chat_id,
            text="Bad, write why the conversation hasn't happened:",
            reply_markup=ReplyKeyboardRemove()
        )
    
    return States.SAVE_FEEDBACK


def save_feedback(update: Update, context: CallbackContext):
    """ pass """
    chat_id = update.message.chat.id
    mssg = update.message.text

    if mssg in ["1", "2", "3", "4", "5"]:
        """ conv has been """
        print("conv ha been")
        pass
    else:
        """ conv has not been"""
        print("conv has not been")
        pass
    context.bot.send_message(
        chat_id=chat_id,
        text="Thanks kindly for your feedback!",
        reply_markup=ReplyKeyboardRemove()
    )
    
    return start(update, context)

