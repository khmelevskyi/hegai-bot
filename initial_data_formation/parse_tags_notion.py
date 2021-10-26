import os

import pandas as pd
import requests
from bot.db_functions import db_session
from sqlalchemy import create_engine


DATABASE_ID = "256d91086c1e4c6c94e449f08fc40ce3"
NOTION_URL = "https://api.notion.com/v1/databases/"

engine = create_engine("postgresql://postgres:dsfdfe34@localhost:5432/hegai-bot")


class ApiError(Exception):
    """An API Error Exception"""

    def __init__(self, status):
        self.status = status

    def __str__(self):
        return "APIError: status={}".format(self.status)


class NotionSync:
    """ class for notion functions """

    def __init__(self):
        """ initial data """
        self.properties_data = {}

        self.properties_data["notion_id"] = []
        self.properties_data["status"] = []
        self.properties_data["name"] = []

    def query_databases(
        self,
        integration_token=os.getenv("NOTION_KEY"),
        start_cursor=None,
    ):
        """ gets info from notion """
        database_url = NOTION_URL + DATABASE_ID + "/query"
        if start_cursor == None:
            response = requests.post(
                database_url,
                headers={
                    "Authorization": f"Bearer {integration_token}",
                    "Notion-Version": "2021-08-16",
                    "Content-Type": "application/json",
                },
                json={"page_size": 100},
            )
        else:
            response = requests.post(
                database_url,
                headers={
                    "Authorization": f"Bearer {integration_token}",
                    "Notion-Version": "2021-08-16",
                    "Content-Type": "application/json",
                },
                json={"start_cursor": start_cursor},
            )

        if response.status_code != 200:
            raise ApiError(f"Response Status: {response.status_code}")
        else:
            return response.json()

    def get_properties_titles(self, data_json):
        """ parses properties of tag object """
        return list(data_json["results"][0]["properties"].keys())

    def get_properties_data(self, data_json, properties):
        """ gets needed data of tag object """
        for ii in range(1, len(data_json["results"])):

            try:
                name = data_json["results"][ii]["properties"]["Focus"]["title"][0][
                    "text"
                ]["content"]
            except IndexError:
                continue

            tag_notion_id = data_json["results"][ii]["id"]
            self.properties_data["notion_id"].append(tag_notion_id)

            for p in properties:
                if p == "Status":

                    try:
                        status = data_json["results"][ii]["properties"][p]["select"][
                            "name"
                        ]
                    except TypeError:
                        status = None

                    self.properties_data["status"].append(status)

                elif p == "Focus":

                    name = data_json["results"][ii]["properties"][p]["title"][0][
                        "text"
                    ]["content"]
                    print(name)

                    self.properties_data["name"].append(name)

        return self.properties_data


nsync = NotionSync()

data = nsync.query_databases()
properties = nsync.get_properties_titles(data)
properties_data = nsync.get_properties_data(data, properties)

has_more = data["has_more"]
while has_more is True:
    start_cursor = data["next_cursor"]
    print(start_cursor)
    data = nsync.query_databases(start_cursor=start_cursor)
    has_more = data["has_more"]
    properties = nsync.get_properties_titles(data)
    properties_data = nsync.get_properties_data(data, properties)


def check_existence(notion_id):
    """ checks whether tag with this notion_id exists """
    query = "SELECT EXISTS (SELECT 1 FROM public.tag WHERE notion_id = %s);"
    return list(engine.execute(query, (notion_id,)))[0][0] == 1


tags_df = pd.DataFrame.from_dict(properties_data)
print(tags_df)


def update_object(obj, new_obj, notion_id):
    """ updating tag if exists """
    obj_dict = obj.__dict__
    dict_keys = new_obj.keys()
    for dict_key in dict_keys:
        if obj_dict[dict_key] != new_obj[dict_key]:
            query = f"UPDATE public.tag SET {dict_key} = '{new_obj[dict_key]}' WHERE notion_id = '{notion_id}';"
            # print(query)
            engine.execute(
                query,
            )
        else:
            pass


def object_to_sql(new_obj):
    """ creating a new row with tag if doesn't exists """
    dict_keys = new_obj.keys()
    str_t = str(tuple([dict_key for dict_key in dict_keys])).replace("'", "")
    query = f"INSERT INTO public.tag {str_t} VALUES{tuple([str(new_obj[dict_key]) for dict_key in dict_keys])};"
    # print(query)
    engine.execute(
        query,
    )


for indx, ii in tags_df.iterrows():
    notion_id = ii["notion_id"]
    # print(notion_id)
    is_exists = check_existence(notion_id)
    # print(is_exists)
    if is_exists == True:
        tag = db_session.get_tag_by_notion_id(notion_id)
        update_object(tag, ii, notion_id)
    elif is_exists == False:
        object_to_sql(ii)
