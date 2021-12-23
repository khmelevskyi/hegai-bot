""" basic info abount user and registrarion process for student and teacher """
import os
import requests

from sqlalchemy import create_engine
from telegram import ParseMode
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import Update
from telegram.ext import CallbackContext
from loguru import logger
from dotenv import load_dotenv

from ...db_functions import Action
from ...data import start_keyboard
from ...data import text
from ...db_functions import db_session
from ...states import States
from .utils import users

load_dotenv()

# from ...db_functions import Action


def profile(update: Update, context: CallbackContext):
    """ basic account info """
    logger.info("showing profile")
    try:
        chat_id = update.message.chat.id
    except AttributeError:
        chat_id = update.callback_query.message.chat.id

    if chat_id in users:  # if user returned from registration form
        users.pop(chat_id, None)

    db_session.log_action(chat_id=chat_id, action=Action.profile)

    user = db_session.get_user_data(chat_id)

    props = get_profile(update, context, user.notion_id)
    if props == None:
        return States.MENU

    cities = str(props["cities"]).replace("'", "").replace("[", "").replace("]", "")
    functions = (
        str(props["Function"]).replace("'", "").replace("[", "").replace("]", "")
    )
    hobbies = str(props["Hobby"]).replace("'", "").replace("[", "").replace("]", "")
    industries = (
        str(props["Industry"]).replace("'", "").replace("[", "").replace("]", "")
    )
    communities = (
        str(props["Related to Focus (Лидер микросообщества)"])
        .replace("'", "")
        .replace("[", "")
        .replace("]", "")
    )

    # db_session.log_action(chat_id=chat_id, action=Action.profile)

    if user.notion_id is None:
        context.bot.send_message(chat_id=chat_id, text=text["not_registered"])
        return States.MENU

    conv_open = user.conversation_open
    if conv_open is True:
        conv_open = "Открыт к разговору"
    else:
        conv_open = "Не открыт к разговору"

    div = 30
    info = (
        f"<i>{user.full_name}</i>\n"
        + f"{text['account_n']} @{user.username}\n"
        + f"Города: {cities}\n"
        + f"<i>id </i>: {chat_id}\n"
        # + f"<i>notion id </i>: {user.notion_id}\n"
        + "-" * div
        + f"\nСтатус: <b>{conv_open}</b>\n"
        + f"\n<b>Компетенции:</b> {functions}"
        + f"\n<b>Хобби:</b> {hobbies}"
        + f"\n<b>Отрасли:</b> {industries}"
        + f"\n<b>Микросообщества, в которых я состою:</b> {communities}\n"
        # + f"\nС нами с: {user.time_registered}\n"
        + "~" * (div // 2)
        + "\n"
    )

    reply_keyboard = [
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
    context.bot.send_message(
        chat_id=chat_id,
        text="Если вы хотите поменять информацию в своем профиле напишите администраторам в @Hegaibot\n",
        reply_markup=markup,
        parse_mode=ParseMode.HTML,
    )
    return States.ACCOUNT


### change status
def change_status(update: Update, context: CallbackContext):
    """ edits user's status """
    logger.info("changing status")

    chat_id = update.message.chat.id

    user = db_session.get_user_data(chat_id)

    if user.conversation_open is True:
        status_text = "Не открыт к разговору"
    else:
        status_text = "Открыт к разговору"

    reply_keyboard = [
        [text["yes"]],
        [text["cancel"]],
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, selective=True)

    context.bot.send_message(
        chat_id=chat_id,
        text=f"Поменять статус на: <b>{status_text}</b>?",
        reply_markup=markup,
        parse_mode=ParseMode.HTML,
    )

    return States.CHANGE_STATUS


def change_status_save(update: Update, context: CallbackContext):
    """ saves new user's status """

    chat_id = update.message.chat.id

    context.bot.send_message(
        chat_id=chat_id, text=text["edit_success"], reply_markup=ReplyKeyboardRemove()
    )

    db_session.save_new_status(chat_id)

    return profile(update, context)


def start_markup() -> ReplyKeyboardMarkup:
    """ markup for start keyboard """
    markup = ReplyKeyboardMarkup(
        keyboard=start_keyboard, resize_keyboard=True, selective=True
    )
    return markup


NOTION_URL = "https://api.notion.com/v1/pages/"

db_username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
database = os.getenv("DB_DATABASE")

engine = create_engine(
    f"postgresql://{db_username}:{password}@{host}:{port}/{database}"
)


class ApiError(Exception):
    """An API Error Exception"""

    def __init__(self, status):
        self.status = status

    def __str__(self):
        return "APIError: status={}".format(self.status)


class NotionSync:
    """ object with data from notion """

    def __init__(self):
        """ init """
        self.properties_data = {}

        self.properties_data["notion_id"] = []
        self.properties_data["username"] = []
        self.properties_data["full_name"] = []
        self.properties_data["cities"] = []
        self.properties_data["Hobby"] = []
        self.properties_data["Function"] = []
        self.properties_data["Industry"] = []
        self.properties_data["Тег"] = []
        self.properties_data["Related to Focus (Лидер микросообщества)"] = []

    def query_databases(self, notion_id, integration_token=os.getenv("NOTION_KEY")):
        """ queries the databases """
        try:
            database_url = NOTION_URL + notion_id.replace("-", "")
        except AttributeError:
            raise ApiError
        response = requests.get(
            database_url,
            headers={
                "Authorization": f"Bearer {integration_token}",
                "Notion-Version": "2021-08-16",
            },
        )

        if response.status_code != 200:
            raise ApiError(f"Response Status: {response.status_code}")
        else:
            return response.json()

    def get_properties_titles(self, data_json):
        """ returns all the property titles of an object """
        return list(data_json["properties"].keys())

    def get_properties_data(self, data_json, properties):
        """ returns all the data for all objects """
        notion_id = data_json["id"]
        self.properties_data["notion_id"].append(notion_id)

        for p in properties:
            if p == "Telegram":

                url = data_json["properties"][p]["url"]
                if url == None:
                    url = None
                elif "t.me" in url and "https" in url:
                    url = url.replace("https://t.me/", "")
                elif "t.me" in url and "https" not in url:
                    url = url.replace("t.me/", "")
                elif "http" in url:
                    url = url.replace("https://", "")
                elif "@" in url:
                    url = url.replace("@", "")
                self.properties_data["username"].append(url)

            elif p == "Name":
                name = data_json["properties"][p]["title"][0]["text"]["content"]
                self.properties_data["full_name"].append(name)

            elif p == "Города":
                elems = data_json["properties"][p]["multi_select"]
                for elem in elems:
                    name = elem["name"]
                    self.properties_data["cities"].append(name)

            elif p in [
                "Hobby",
                "Function",
                "Industry",
                "Тег",
                "Related to Focus (Лидер микросообщества)",
            ]:
                elems = data_json["properties"][p]["relation"]
                for elem in elems:
                    tag_notion_id = elem["id"]
                    try:
                        name = db_session.get_tag_by_notion_id(tag_notion_id).name
                    except AttributeError:
                        continue
                    self.properties_data[p].append(name)

        return self.properties_data


def get_profile(update: Update, context: CallbackContext, notion_id):
    """ returns the profile info of an user """
    nsync = NotionSync()

    try:
        data = nsync.query_databases(notion_id)
        properties = nsync.get_properties_titles(data)
        properties_data = nsync.get_properties_data(data, properties)

        return properties_data
    except ApiError:
        context.bot.send_message(
            chat_id=update.message.chat.id,
            text="К сожалению, возникла ошибка. Возможно у Вас нет страницы в Notion",
            reply_markup=start_markup(),
        )
        return None
