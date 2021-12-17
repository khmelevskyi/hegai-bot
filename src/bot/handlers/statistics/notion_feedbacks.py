""" saves feedbacks to notion """
import os
import requests

from sqlalchemy import create_engine
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


DATABASE_ID = "36b7d151fc614f1bbdaa02daa3ae2aa6"
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


def save_feedback_to_notion(notion_body):
    """ pass """
    nsync = NotionSync()
    logger.info("saving feedback to notion")

    nsync.query_databases(notion_body)
    logger.info("feedback saved to notion✅")
