""" basic info abount user and registrarion process for student and teacher """
from telegram import ParseMode
from telegram import Update
from telegram.ext import CallbackContext

from ...data import text
from ...db_functions import db_session
from ...states import States

# from ...db_functions import Action


def my_contacts(update: Update, context: CallbackContext):
    """ sends info about user's contacts """

    chat_id = update.message.chat.id

    user = db_session.get_user_data(chat_id)

    # db_session.log_action(chat_id=chat_id, action=Action.profile)

    if user.notion_id is None:
        context.bot.send_message(
            chat_id=update.message.chat.id, text=text["not_registered"]
        )
        return States.MENU

    contacts = db_session.get_contacts(user.id)

    contacts_info = ""
    for ii in contacts:
        user = db_session.get_user_data_by_id(ii)
        contacts_info += f"{user.full_name} - @{user.username}\n"
        contacts_info += f"{('~'*30)}\n"

    if contacts == []:
        contacts_info = "На данный момент у Вас нет контактов!"

    info = (
        "<i>Это люди, с кем у вас была пара в Hegai Random Coffee и в этом боте</i>\n\n"
        + contacts_info
    )

    context.bot.send_message(
        chat_id=chat_id,
        text=info,
        parse_mode=ParseMode.HTML,
    )
