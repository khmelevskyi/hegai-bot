""" ask for feedback module """
import json
from os import getenv
from datetime import timedelta, datetime
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
    inline_soda_buttons = [
        InlineKeyboardButton(text["feedback_never"], callback_data="feedback_never")
    ]

    for conv_request in conv_requests:
        user_id = conv_request.user_id
        user_found_id = conv_request.user_found
        for_feedback_times_asked = conv_request.feedback_times_asked

        if for_feedback_times_asked == 0:
            markup = InlineKeyboardMarkup(
                [inline_limonad_button, inline_compot_buttons],
                resize_keyboard=True,
                one_time_keyboard=True,
            )
            db_session.increment_feedback_times_asked(conv_request.id)
        elif (
            for_feedback_times_asked == 1
            and conv_request.time_posted <= datetime.now() - timedelta(days=6)
        ):
            markup = InlineKeyboardMarkup(
                [inline_limonad_button, inline_compot_buttons, inline_soda_buttons],
                resize_keyboard=True,
                one_time_keyboard=True,
            )
            db_session.increment_feedback_times_asked(conv_request.id)
        else:
            continue

        user_one = db_session.get_user_data_by_id(user_id)
        user_found = db_session.get_user_data_by_id(user_found_id)

        try:
            if for_feedback_times_asked == 0:
                context.bot.send_message(
                    chat_id=user_one.chat_id,
                    text=f"Пришло время фидбека!\nПроизошел ли Ваш разговор с @{user_found.username}?",
                    reply_markup=markup,
                )
            elif for_feedback_times_asked == 1:
                context.bot.send_message(
                    chat_id=user_one.chat_id,
                    text=f"Напоминаем про фидбек!\nПроизошел ли Ваш разговор с @{user_found.username}?",
                    reply_markup=markup,
                )
        except Exception as e:
            logger.error(f"Error while mailing feedback: {e}")

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
    elif mssg == "feedback_no":
        context.user_data["is_feedback_yes"] = False
        context.bot.send_message(
            chat_id=chat_id,
            text="Очень жаль(\nНапишите почему беседа не состоялась:",
            reply_markup=ReplyKeyboardRemove(),
        )
    elif mssg == "feedback_never":
        context.user_data["is_feedback_yes"] = "never"
        context.bot.send_message(
            chat_id=chat_id,
            text="Очень жаль(\nНапишите причину, пожалуйста:",
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
        ] = user_found.username  # maybe change to reference
        notion_body["properties"]["Occured"]["checkbox"] = True
        notion_body["properties"]["Comment"]["rich_text"][0]["text"]["content"] = mssg

        save_feedback_to_notion(json.dumps(notion_body))

    elif context.user_data["is_feedback_yes"] == False:
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
        ] = user_found.username  # maybe change to reference
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

    elif context.user_data["is_feedback_yes"] == "never":
        conv_request = db_session.get_conv_request_more_3_days_active_by_chat_id(
            chat_id
        )
        db_session.make_conv_request_inactive(conv_request.id)
        db_session.create_not_success_feedback(
            conv_request.id, "Не будут встречаться, причина:\n" + mssg
        )

        user_one = db_session.get_user_data(chat_id)
        user_found = db_session.get_user_data_by_id(conv_request.user_found)

        user_one = db_session.get_user_data(chat_id)
        user_found = db_session.get_user_data_by_id(conv_request.user_found)
        logger.info(
            f"feedback: conv between @{user_one.username} and @{user_found.username} NOT been after second reminder"
        )
        notion_body = json.loads(json_body)
        notion_body["properties"]["Name"]["title"][0]["text"][
            "content"
        ] = user_one.username
        notion_body["properties"]["Reference"]["relation"][0]["id"] = user_one.notion_id
        notion_body["properties"]["With"]["rich_text"][0]["text"][
            "content"
        ] = user_found.username  # maybe change to reference
        notion_body["properties"]["Occured"]["checkbox"] = False
        notion_body["properties"]["Comment"]["rich_text"][0]["text"]["content"] = (
            "Не будут встречаться, причина:\n" + mssg
        )
        save_feedback_to_notion(json.dumps(notion_body))

        context.bot.send_message(
            chat_id=getenv("GROUP_ID"),
            text=(
                f"Диалог между @{user_one.username} и @{user_found.username} не состоялся\n"
                + f"По словам @{user_one.username}:\n"
                + "<i>Не будут встречаться, причина:</i>"
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
