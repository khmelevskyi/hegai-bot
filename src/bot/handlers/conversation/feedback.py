""" ask for feedback module """
from os import getenv
from telegram import ParseMode
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import Update
from telegram.ext import CallbackContext

from ...data import text
from ...db_functions import db_session
from ...states import States
from ..handlers import start


def ask_feedback(*args):
    """ asks for user's feedback 3 days after a conversation """

    context = args[0]

    conv_requests = db_session.get_conv_requests_more_3_days_active()
    print(conv_requests)

    inline_limonad_button = [
        InlineKeyboardButton(text["yes"], callback_data="feedback_yes")
    ]
    inline_compot_buttons = [
        InlineKeyboardButton(text["no"], callback_data="feedback_no")
    ]

    markup = InlineKeyboardMarkup(
        [inline_limonad_button, inline_compot_buttons],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    for conv_request in conv_requests:
        user_id = conv_request.user_id
        user_found_id = conv_request.user_found

        user_one = db_session.get_user_data_by_id(user_id)
        user_found = db_session.get_user_data_by_id(user_found_id)

        context.bot.send_message(
            chat_id=user_one.chat_id,
            text=f"Пришло время фидбека!\nПроизошел ли Ваш разговор с @{user_found.username}?",
            reply_markup=markup,
        )

    # return States.ASK_FEEDBACK


def ask_feedback_result(update: Update, context: CallbackContext):
    """ asks for an estimation of a conversation or its absence explanation """

    chat_id = update.effective_chat.id
    mssg = update.callback_query.data
    update.callback_query.answer()
    print(mssg)

    if mssg == "feedback_yes":

        reply_keyboard = [["1", "2"], ["3", "4"], ["5"]]
        markup = ReplyKeyboardMarkup(
            reply_keyboard, resize_keyboard=True, selective=True
        )

        context.bot.send_message(
            chat_id=chat_id,
            text="Отлично! Оцените беседу от 1 до 5:",
            reply_markup=markup,
        )
    else:
        context.bot.send_message(
            chat_id=chat_id,
            text="Очень жаль(\nНапишите почему беседа не состоялась:",
            reply_markup=ReplyKeyboardRemove(),
        )

    return States.SAVE_FEEDBACK


def save_feedback(update: Update, context: CallbackContext):
    """ pass """
    chat_id = update.message.chat.id
    mssg = update.message.text

    if mssg in ["1", "2", "3", "4", "5"]:
        print("conv ha been")
        conv_request = db_session.get_conv_request_more_3_days_active_by_chat_id(
            chat_id
        )
        db_session.make_conv_request_inactive(conv_request.id)
        db_session.create_success_feedback(conv_request.id, int(mssg))
    else:
        print("conv has not been")
        conv_request = db_session.get_conv_request_more_3_days_active_by_chat_id(
            chat_id
        )
        db_session.make_conv_request_inactive(conv_request.id)
        db_session.create_not_success_feedback(conv_request.id, mssg)

        user_one = db_session.get_user_data(chat_id)
        user_found = db_session.get_user_data_by_id(conv_request.user_found)

        context.bot.send_message(
            chat_id=getenv("GROUP_ID"),
            text=(
                f"Диалог между @{user_one.username} и @{user_found.username} не состоялся\n"
                + f"Причина по словам @{user_one.username}:\n"
                + f"<i>{mssg}</i>"
            ),
            parse_mode=ParseMode.HTML,
        )

    context.bot.send_message(
        chat_id=chat_id,
        text="Спасибо за Ваш ответ!",
        reply_markup=ReplyKeyboardRemove(),
    )

    return start(update, context)
