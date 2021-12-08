""" Commands interface """
from loguru import logger
from telegram import Bot
from telegram import BotCommandScopeAllChatAdministrators
from telegram import BotCommandScopeAllGroupChats
from telegram import BotCommandScopeAllPrivateChats
from telegram import BotCommandScopeChat
from .db_functions import db_session

ADMIN_IDS = [
    db_session.get_user_data_by_id(admin_id).chat_id
    for admin_id in db_session.get_admins()
]


def clear_bot(bot: Bot):
    """deletes previous commands"""

    bot.delete_my_commands(BotCommandScopeAllPrivateChats())
    bot.delete_my_commands(BotCommandScopeAllGroupChats())
    bot.delete_my_commands(BotCommandScopeAllChatAdministrators())
    logger.debug("User commands were cleared.")


all_commands = [
    ("start", "Старт/Рестарт ▶"),
    ("help", "Помощь ❓"),
]

admin_commands = [
    ("admin", "Меню администратора ☢"),
]


def set_bot_commands(bot: Bot):
    """create commands lists for different chats and users"""

    # admins
    for chat_id in ADMIN_IDS:
        try:
            bot.set_my_commands(
                all_commands + admin_commands, scope=BotCommandScopeChat(chat_id)
            )
        except Exception as error:
            logger.error(
                f"Setting commands for chat_id: {chat_id}, failed with error: {error}"
            )

    # privat chats
    bot.set_my_commands(all_commands, scope=BotCommandScopeAllPrivateChats())

    # group admins
    bot.set_my_commands(all_commands, scope=BotCommandScopeAllChatAdministrators())

    #
    bot.set_my_commands(
        [
            ("start", "Старт/Рестарт ▶"),
            ("help", "Помощь ❓"),
        ],
        scope=BotCommandScopeAllGroupChats(),
    )

    logger.debug("Command list was updated.")
