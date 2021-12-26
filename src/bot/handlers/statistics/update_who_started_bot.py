""" saves feedbacks to notion """
import os
import requests

from sqlalchemy import create_engine
from loguru import logger
from dotenv import load_dotenv

from ...db_functions import db_session

load_dotenv()


NOTION_URL_PAGES = "https://api.notion.com/v1/pages/"
NOTION_URL_DATABASES = "https://api.notion.com/v1/databases/"
WHO_STARTED_BOT_DATABASE = "b6041b1bc4c04b91a2d850b9693c5fc2"

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

    def get_data(
        self,
        notion_id,
        integration_token=os.getenv("NOTION_KEY"),
    ):
        """ queries the databases """
        database_url = NOTION_URL_DATABASES + WHO_STARTED_BOT_DATABASE + "/query"
        response = requests.post(
            database_url,
            headers={
                "Authorization": f"Bearer {integration_token}",
                "Notion-Version": "2021-08-16",
                "Content-Type": "application/json",
            },
            json={
                "filter": {"property": "Reference", "relation": {"contains": notion_id}}
            },
        )

        if response.status_code != 200:
            raise ApiError(
                f"Response Status: {response.status_code}, {response.content}"
            )
        else:
            return response.json()

    def proccess_data(self, data):
        """ takes notion id from a link """
        page_id = data["results"][0]["url"]
        page_id = page_id.replace("https://www.notion.so/", "")
        page_id = (
            page_id[:8]
            + "-"
            + page_id[8:12]
            + "-"
            + page_id[12:16]
            + "-"
            + page_id[16:20]
            + "-"
            + page_id[20:32]
        )
        return page_id

    def query_databases(
        self,
        page_id,
        is_conv_open,
        integration_token=os.getenv("NOTION_KEY"),
    ):
        """ queries the databases """
        database_url = NOTION_URL_PAGES + page_id

        response = requests.patch(
            database_url,
            headers={
                "Authorization": f"Bearer {integration_token}",
                "Notion-Version": "2021-08-16",
                "Content-Type": "application/json",
            },
            json={"properties": {"Conversation_open": {"checkbox": is_conv_open}}},
        )

        if response.status_code != 200:
            raise ApiError(
                f"Response Status: {response.status_code}, {response.content}"
            )
        else:
            return response.json()


def update_user_started_bot_to_notion(chat_id):
    """ pass """
    nsync = NotionSync()
    logger.info(f"updating conv status for user ({chat_id})")

    user = db_session.get_user_data(chat_id)

    data = nsync.get_data(user.notion_id)
    page = nsync.proccess_data(data)
    nsync.query_databases(page, user.conversation_open)
