import os
from dotenv import load_dotenv
import pandas as pd
import requests
from sqlalchemy import create_engine

from ...db_functions import db_session

load_dotenv()

DATABASE_ID = "256d91086c1e4c6c94e449f08fc40ce3"
NOTION_URL = "https://api.notion.com/v1/databases/"

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
    def __init__(self):
        self.properties_data = {}

    def query_databases(
        self,
        property_type,
        integration_token=os.getenv("NOTION_KEY"),
        start_cursor=None,
    ):
        database_url = NOTION_URL + DATABASE_ID + "/query"
        if start_cursor == None:
            response = requests.post(
                database_url,
                headers={
                    "Authorization": f"Bearer {integration_token}",
                    "Notion-Version": "2021-08-16",
                    "Content-Type": "application/json",
                },
                json={
                    "filter": {
                        "property": property_type,
                        "multi_select": {"is_not_empty": True},
                    }
                },
            )
        else:
            response = requests.post(
                database_url,
                headers={
                    "Authorization": f"Bearer {integration_token}",
                    "Notion-Version": "2021-08-16",
                    "Content-Type": "application/json",
                },
                json={
                    "start_cursor": start_cursor,
                    "filter": {
                        "property": property_type,
                        "multi_select": {"is_not_empty": True},
                    },
                },
            )
        if response.status_code != 200:
            raise ApiError(f"Response Status: {response.status_code}")
        else:
            return response.json()

    def get_properties_titles(self, data_json):
        return list(data_json["results"][0]["properties"].keys())

    def get_properties_data(self, data_json, property_type):
        for ii in range(1, len(data_json["results"])):

            try:
                status = data_json["results"][ii]["properties"][property_type][
                    "multi_select"
                ][0]["name"]
                if status not in self.properties_data.keys():
                    self.properties_data[status] = []
                    name = data_json["results"][ii]["properties"]["Focus"]["title"][0][
                        "text"
                    ]["content"]
                    self.properties_data[status].append(name)
                else:
                    name = data_json["results"][ii]["properties"]["Focus"]["title"][0][
                        "text"
                    ]["content"]
                    self.properties_data[status].append(name)
            except TypeError:
                status = None

        return self.properties_data


def check_existence(name):
    query = "SELECT EXISTS (SELECT 1 FROM public.tag WHERE name = %s);"
    return list(engine.execute(query, (name,)))[0][0] == 1


def object_to_sql(name, status):
    query = f"INSERT INTO public.tag (name, notion_id, status) VALUES ('{name}', 1, '{status}');"
    print(query)
    engine.execute(
        query,
    )


def parse_tags_groups(*args):
    props = ["Компетенция", "Отрасль"]
    general_df = {}

    for prop in props:
        nsync = NotionSync()
        data = nsync.query_databases(property_type=prop)
        properties = nsync.get_properties_titles(data)
        properties_data = nsync.get_properties_data(data, property_type=prop)

        has_more = data["has_more"]
        while has_more is True:
            start_cursor = data["next_cursor"]
            print(start_cursor)
            data = nsync.query_databases(start_cursor=start_cursor)
            has_more = data["has_more"]
            properties = nsync.get_properties_titles(data)
            properties_data = nsync.get_properties_data(data, properties)

        if prop == "Компетенция":
            expertise_df = properties_data
            for tag in expertise_df.keys():
                is_exists = check_existence(tag)
                if is_exists is True:
                    pass
                else:
                    object_to_sql(tag, "Компетенции")
        elif prop == "Отрасль":
            industry_df = properties_data
            for tag in industry_df.keys():
                is_exists = check_existence(tag)
                if is_exists is True:
                    pass
                else:
                    object_to_sql(tag, "Отрасли")

    general_df = {**expertise_df, **industry_df}
    return expertise_df, industry_df
