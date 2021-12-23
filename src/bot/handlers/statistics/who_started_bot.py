""" saves feedbacks to notion """
import os
import json
import requests

from sqlalchemy import create_engine
from loguru import logger
from dotenv import load_dotenv

from ...db_functions import db_session

load_dotenv()


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


json_body = """
{
    "parent": { "database_id": "b6041b1bc4c04b91a2d850b9693c5fc2" },
    "properties": {
        "Name": {
            "title": [
                {
                    "text": {
                        "content": "full_name"
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
        "When": {
            "date": {
                "start": ""
            }
        }
    }
}
"""


class NotionSync:
    """ object with data from notion """

    def __init__(self):
        """ init """
        self.properties_data = {}

    def query_databases(
        self,
        notion_body,
        integration_token=os.getenv("NOTION_KEY"),
    ):
        """ queries the databases """
        database_url = NOTION_URL
        response = requests.post(
            database_url,
            headers={
                "Authorization": f"Bearer {integration_token}",
                "Notion-Version": "2021-08-16",
                "Content-Type": "application/json",
            },
            data=notion_body,
        )

        if response.status_code != 200:
            raise ApiError(f"Response Status: {response.status_code}")
        else:
            return response.json()


def save_user_started_bot_to_notion(chat_id):
    """ pass """
    nsync = NotionSync()
    logger.info(f"user ({chat_id}) started the bot")

    user = db_session.get_user_data(chat_id)

    notion_body = json.loads(json_body)
    notion_body["properties"]["Name"]["title"][0]["text"]["content"] = user.full_name
    notion_body["properties"]["Reference"]["relation"][0]["id"] = user.notion_id
    notion_body["properties"]["When"]["date"]["start"] = str(user.time_registered)

    try:
        if user.notion_id != None or len(user.notion_id) > 5:
            nsync.query_databases(json.dumps(notion_body))
    except TypeError:
        pass
