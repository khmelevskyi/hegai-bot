""" basic info abount user and registrarion process for student and teacher """
from telegram import ParseMode
from telegram import ReplyKeyboardMarkup
from telegram import Update
from telegram.ext import CallbackContext

from ...db_functions import Action
from ...db_functions import db_session
from ...data import text
from ...states import States


def profile(update: Update, context: CallbackContext):
    """ basic account info """

    chat_id = update.message.chat.id

    # if chat_id in users:  # if user returned from registration form
    #     users.pop(chat_id, None)

    # db_session.log_action(chat_id=chat_id, action=Action.profile)

    # university_id, user_data = db_session.get_user_data(chat_id=chat_id)
    # if university_id is None:
    #     context.bot.send_message(
    #         chat_id=update.message.chat.id, text=text["not_registered"]
    #     )
    #     return States.MENU
    # university = "this" # cached_data.list_universities()[university_id][0]
    # info = f'<i>{text["university_n"]}</i>{university}\n'

    # if user_data["type"] == "student":
    #     user_type = text["student_q"]
    # else:
    #     user_type = text["teacher_q"]

    # admins = ""

    # username = update.message.chat.username
    # if username:
    #     username = "@" + username
    # else:
    #     username = ""
    # div = 30
    # info = (
    #     f"{text['account_n']} {username}\n"
    #     + f"<i>id </i>: {chat_id}\n"
    #     + "-" * div
    #     + f"\n<b>{user_type}</b>{admins}\n"
    #     + f"\n{info}\n"
    #     + "~" * (div // 2)
    #     + "\n"
    #     + text["more_info"]
    # )

    info = "user profile"

    reply_keyboard = [
        [text["admin_menu"]],
        [text["change_button"]],
        [text["back"]],
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, selective=True)

    context.bot.send_message(
        chat_id=chat_id,
        text=info,
        reply_markup=markup,
        parse_mode=ParseMode.HTML,
    )
    return States.ACCOUNT
