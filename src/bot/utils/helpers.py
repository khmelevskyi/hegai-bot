""" commonly used functions """
from typing import List
from typing import Optional
from typing import Union

from telegram import Bot
from telegram import ReplyKeyboardMarkup
from telegram import Update
from telegram.chat import Chat

from ..data import text


def generate_markup(
    options: Union[dict, list, None] = None,
    columns: int = 1,  # vertical default
    base_options: Optional[list] = None,
    top_down: bool = True,
) -> ReplyKeyboardMarkup:
    """Generaty keyboard markup for registration options
    Args:
        options (dict): button options
        columns (int): number of columns
        base_options (list): predefined options
        top_down(bool): if True place base_options on top
    Returns:
        ReplyKeyboardMarkup: markup
    """
    base_options = base_options if base_options else [[text["back"]]]
    reply_keyboard = base_options if top_down else []

    if options:
        buttons = options.keys() if isinstance(options, dict) else options

        if columns == 1:
            reply_keyboard += [[i] for i in buttons]
        else:
            options_last_index = len(buttons) - 1
            row = []
            for i, value in enumerate(buttons):
                row.append(value)
                if len(row) == columns or i == options_last_index:
                    reply_keyboard.append(list(row))
                    row.clear()

    if not top_down:
        reply_keyboard += base_options

    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, selective=True)
    return markup


def send_msg(
    update: Update,
    msg_text: str,
    markup: ReplyKeyboardMarkup = None,
):
    """
    in group reply to message
    in privat chat send directly
    """

    kwargs = {"text": msg_text}
    if markup:
        kwargs["reply_markup"] = markup
    if update.message.chat.type != Chat.PRIVATE:
        kwargs["reply_to_message_id"] = update.message.message_id
    update.message.reply_text(**kwargs)
    # context.bot.send_message(**kwargs)


def get_group_admins(bot: Bot, chat_id: int) -> List[str]:
    """List chat admin by username or id link
    Args:
        bot (Bot): telegram bot
        chat_id (int): group id
    Returns:
        List[str]: list admins
    """
    group_admins = bot.get_chat_administrators(chat_id)
    admin_list = []
    for admin in group_admins:
        if admin.user.username:
            mention = "@" + admin.user.username
        else:
            admin_id = admin.user.id
            mention = (
                f"<a href='tg://user?id={admin_id}'>"
                + f"{admin.user.first_name} {admin.user.last_name}</a>"
            )
        admin_list.append(mention)
    return admin_list


def get_chat_msg(update: Update):
    """ retruves chat id and msg text from upfate """
    chat_id = update.message.chat.id
    msg = update.message.text
    return chat_id, msg
