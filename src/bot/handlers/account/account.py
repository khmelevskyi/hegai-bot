""" basic info abount user and registrarion process for student and teacher """
from telegram import ParseMode
from telegram import ReplyKeyboardMarkup
from telegram import Update
from telegram.ext import CallbackContext

# from ...db_functions import Action
from ...db_functions import db_session
from ...data import text
from ...states import States
from .utils import users


def profile(update: Update, context: CallbackContext):
    """ basic account info """

    chat_id = update.message.chat.id

    if chat_id in users:  # if user returned from registration form
        users.pop(chat_id, None)

    user = db_session.get_user_data(chat_id)

    # db_session.log_action(chat_id=chat_id, action=Action.profile)

    if user.notion_id is None:
        context.bot.send_message(
            chat_id=update.message.chat.id, text=text["not_registered"]
        )
        return States.MENU

    conv_open = user.conversation_open
    if conv_open == True:
        conv_open = "Открыт к разговору"
    else:
        conv_open = "Не открыт к разговору"
    div = 30
    info = (
        f"<i>{user.full_name}</i>\n"
        + f"{text['account_n']} @{user.username}\n"
        + f"Регион: {user.region}\n"
        + f"<i>id </i>: {chat_id}\n"
        # + f"<i>notion id </i>: {user.notion_id}\n"
        + "-" * div
        + f"\nСтатус: <b>{conv_open}</b>\n"
        # + f"\nС нами с: {user.time_registered}\n"
        + "~" * (div // 2)
        + "\n"
        + text["more_info"]
    )

    reply_keyboard = [
        [text["change_name"], text["change_region"]],
        [text["change_status"]],
        [text["main_menu"]],
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, selective=True)

    context.bot.send_message(
        chat_id=chat_id,
        text=info,
        reply_markup=markup,
        parse_mode=ParseMode.HTML,
    )
    return States.ACCOUNT
