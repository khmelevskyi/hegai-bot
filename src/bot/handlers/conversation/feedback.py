""" ask for feedback module """
import json
from os import getenv
from telegram import ParseMode
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import Update
from telegram.ext import CallbackContext
from loguru import logger

from ...data import text
from ...db_functions import db_session
from ...states import States
from ..handlers import start
from ..statistics import save_feedback_to_notion

json_body = """
{
    "parent": { "database_id": "36b7d151fc614f1bbdaa02daa3ae2aa6" },
    "properties": {
        "Name": {
            "title": [
                {
                    "text": {
                        "content": "username"
                    }
                }
            ]
        },
        "Reference": {
            "relation": [
                {
                    "id": "123"
                }
            ]
        },
        "With": {
            "rich_text": [
                {
                    "text": {
                        "content": "user_found_username"
                    }
                }
            ]
        },
        "Occured": {
            "checkbox": true
        },
        "Comment": {
            "rich_text": [
                {
                    "text": {
                        "content": "comment"
                    }
                }
            ]
        }
    }
}
"""


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
        context.user_data["is_feedback_yes"] = True

        context.bot.send_message(
            chat_id=chat_id,
            text="Мы хотим улучшать качество интро, поэтому нам важна обратная связь.\n\nПожалуйста, поделитесь, насколько это интро соответствовало вашему запросу",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        context.user_data["is_feedback_yes"] = False
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

    if context.user_data["is_feedback_yes"] == True:
        conv_request = db_session.get_conv_request_more_3_days_active_by_chat_id(
            chat_id
        )
        db_session.make_conv_request_inactive(conv_request.id)
        db_session.create_success_feedback(conv_request.id, mssg)

        user_one = db_session.get_user_data(chat_id)
        user_found = db_session.get_user_data_by_id(conv_request.user_found)
        logger.info(
            f"feedback: conv between @{user_one.username} and @{user_found.username} been"
        )
        notion_body = json.loads(json_body)
        notion_body["properties"]["Name"]["title"][0]["text"][
            "content"
        ] = user_one.username
        notion_body["properties"]["Reference"]["relation"][0]["id"] = user_one.notion_id
        notion_body["properties"]["With"]["rich_text"][0]["text"][
            "content"
        ] = user_found.username
        notion_body["properties"]["Occured"]["checkbox"] = True
        notion_body["properties"]["Comment"]["rich_text"][0]["text"]["content"] = mssg

        save_feedback_to_notion(json.dumps(notion_body))

    else:
        conv_request = db_session.get_conv_request_more_3_days_active_by_chat_id(
            chat_id
        )
        db_session.make_conv_request_inactive(conv_request.id)
        db_session.create_not_success_feedback(conv_request.id, mssg)

        user_one = db_session.get_user_data(chat_id)
        user_found = db_session.get_user_data_by_id(conv_request.user_found)

        user_one = db_session.get_user_data(chat_id)
        user_found = db_session.get_user_data_by_id(conv_request.user_found)
        logger.info(
            f"feedback: conv between @{user_one.username} and @{user_found.username} NOT been"
        )
        notion_body = json.loads(json_body)
        notion_body["properties"]["Name"]["title"][0]["text"][
            "content"
        ] = user_one.username
        notion_body["properties"]["Reference"]["relation"][0]["id"] = user_one.notion_id
        notion_body["properties"]["With"]["rich_text"][0]["text"][
            "content"
        ] = user_found.username
        notion_body["properties"]["Occured"]["checkbox"] = False
        notion_body["properties"]["Comment"]["rich_text"][0]["text"]["content"] = mssg
        save_feedback_to_notion(json.dumps(notion_body))

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
