""" basic info abount user and registrarion process for student and teacher """
import os
import requests
import pandas as pd

from sqlalchemy import create_engine
from loguru import logger
from dotenv import load_dotenv

from ...db_functions import db_session

load_dotenv()


DATABASE_ID = "0bfe439187b74e15842803cacc6d38da"
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

    def query_databases(
        self,
        integration_token=os.getenv("NOTION_KEY"),
        start_cursor=None,
    ):
        """ queries the databases """
        database_url = NOTION_URL + DATABASE_ID + "/query"
        if start_cursor == None:
            response = requests.post(
                database_url,
                headers={
                    "Authorization": f"Bearer {integration_token}",
                    "Notion-Version": "2021-08-16",
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
                json={"start_cursor": start_cursor},
            )

        if response.status_code != 200:
            raise ApiError(f"Response Status: {response.status_code}")
        else:
            return response.json()

    def get_properties_titles(self, data_json):
        """ returns all the property titles of an object """
        return list(data_json["results"][0]["properties"].keys())

    def get_properties_data(self, data_json, properties):
        """ returns all the data for all objects """
        for ii in range(1, len(data_json["results"])):
            try:
                name = data_json["results"][ii]["properties"]["Name"]["title"][0][
                    "text"
                ]["content"]
            except IndexError:
                continue

            notion_id = data_json["results"][ii]["id"]
            self.properties_data["notion_id"].append(notion_id)

            for p in properties:
                if p == "Telegram":

                    url = data_json["results"][ii]["properties"][p]["url"]
                    if url == None:
                        url = None
                    elif "t.me" in url and "https" in url:
                        url = url.replace("https://t.me/", "")
                    elif "t.me" in url and "http" not in url:
                        url = url.replace("t.me/", "")
                    elif "http" in url and "t.me" not in url and "https" not in url:
                        url = url.replace("http://", "")
                    elif "https" in url and "t.me" not in url:
                        url = url.replace("https://", "")
                    elif "http://t.me" in url:
                        url = url.replace("http://t.me/", "")
                    elif "@" in url:
                        url = url.replace("@", "")
                    self.properties_data["username"].append(url.lower())

                elif p == "Name":
                    name = data_json["results"][ii]["properties"][p]["title"][0][
                        "text"
                    ]["content"]
                    self.properties_data["full_name"].append(name)

                elif p == "Города":
                    elems = data_json["results"][ii]["properties"][p]["multi_select"]
                    elem_names = []
                    for elem in elems:
                        name = elem["name"]
                        elem_names.append(name)
                    self.properties_data["cities"].append(elem_names)

                elif p in [
                    "Hobby",
                    "Function",
                    "Industry",
                    "Тег",
                    "Related to Focus (Лидер микросообщества)",
                ]:
                    elems = data_json["results"][ii]["properties"][p]["relation"]
                    elem_ids = []
                    for elem in elems:
                        tag_notion_id = elem["id"]
                        try:
                            tag_id = db_session.get_tag_by_notion_id(tag_notion_id).id
                        except AttributeError:
                            continue
                        elem_ids.append(tag_id)
                    self.properties_data[p].append(elem_ids)

        return self.properties_data


def check_existence(notion_id):
    query = (
        f"SELECT EXISTS (SELECT 1 FROM public.user WHERE notion_id = '{notion_id}');"
    )
    return (
        list(engine.execute(query,))[
            0
        ][0]
        == 1
    )


def update_object(obj, new_obj, notion_id):
    obj_dict = obj.__dict__
    dict_keys = new_obj.keys()
    for dict_key in dict_keys:
        if obj_dict[dict_key] != new_obj[dict_key]:
            query = f"UPDATE public.user SET {dict_key} = '{new_obj[dict_key]}' WHERE notion_id = '{notion_id}';"
            print(query)
            engine.execute(
                query,
            )
        else:
            pass


def object_to_sql(new_obj):
    dict_keys = new_obj.keys()
    str_t = str(tuple([dict_key for dict_key in dict_keys])).replace("'", "")
    query = f"INSERT INTO public.user {str_t} VALUES{tuple([str(new_obj[dict_key]) for dict_key in dict_keys])};"
    print(query)
    engine.execute(
        query,
    )


def add_user_tags(new_obj):
    notion_id = new_obj["notion_id"]
    user_tags = db_session.get_user_tags_by_notion_id(notion_id)
    for user_tag in user_tags:
        db_session.remove_user_tag(user_tag.id)
    dict_keys = new_obj.keys()
    for dict_key in dict_keys:
        if dict_key != "notion_id":
            tag_ids = new_obj[dict_key]
            for tag_id in tag_ids:
                db_session.add_user_tag_by_notion_id(notion_id, tag_id)


def add_user_regions(new_obj):
    notion_id = new_obj["notion_id"]
    city_names = new_obj["cities"]
    if "Москва" or "Moscow" in city_names:
        region_id = db_session.get_region_by_name("Москва").id
        db_session.save_new_region(notion_id, region_id)
    else:
        try:
            region_id = db_session.get_region_by_name(city_names[0]).id
            db_session.save_new_region(notion_id, region_id)
        except AttributeError:
            db_session.create_region(city_names[0])
            region_id = db_session.get_region_by_name(city_names[0]).id
            db_session.save_new_region(notion_id, region_id)


def parse_user_tags_notion_update(*args):
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

    users_df = pd.DataFrame.from_dict(properties_data)
    print(users_df)

    for indx, ii in users_df.iterrows():
        notion_id = ii["notion_id"]
        user_obj = ii[["notion_id", "username", "full_name"]]
        user_region_obj = ii[["notion_id", "cities"]]
        user_tags_obj = ii[
            [
                "notion_id",
                "Hobby",
                "Function",
                "Industry",
                "Тег",
                "Related to Focus (Лидер микросообщества)",
            ]
        ]
        # print(notion_id)
        is_exists = check_existence(notion_id)
        # print(is_exists)
        if is_exists is True:
            user = db_session.get_user_data_by_notion_id(notion_id)
            update_object(user, user_obj, notion_id)
        elif is_exists is False:
            object_to_sql(user_obj)

        add_user_tags(user_tags_obj)
        add_user_regions(user_region_obj)
