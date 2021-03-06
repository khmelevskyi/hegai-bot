import os
from dotenv import load_dotenv
import pandas as pd
import requests
from bot.db_functions import db_session
from sqlalchemy import create_engine

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
    def __init__(self):
        self.properties_data = {}

        self.properties_data["notion_id"] = []
        self.properties_data["username"] = []
        self.properties_data["full_name"] = []

    def query_databases(
        self,
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
        return list(data_json["results"][0]["properties"].keys())

    def get_properties_data(self, data_json, properties):
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
                    elif "t.me" in url and "https" not in url:
                        url = url.replace("t.me/", "")
                    elif "http" in url:
                        url = url.replace("https://", "")
                    elif "@" in url:
                        url = url.replace("@", "")
                    self.properties_data["username"].append(url)

                elif p == "Name":

                    name = data_json["results"][ii]["properties"][p]["title"][0][
                        "text"
                    ]["content"]
                    print(name)

                    self.properties_data["full_name"].append(name)

        return self.properties_data


nsync = NotionSync()

data = nsync.query_databases()
properties = nsync.get_properties_titles(data)
properties_data = nsync.get_properties_data(data, properties)

has_more = data["has_more"]
while has_more == True:
    start_cursor = data["next_cursor"]
    print(start_cursor)
    data = nsync.query_databases(start_cursor=start_cursor)
    has_more = data["has_more"]
    properties = nsync.get_properties_titles(data)
    properties_data = nsync.get_properties_data(data, properties)


def check_existence(username):
    query = f"SELECT EXISTS (SELECT 1 FROM public.user WHERE username = '{username}');"
    return (
        list(engine.execute(query,))[
            0
        ][0]
        == 1
    )


users_df = pd.DataFrame.from_dict(properties_data)
print(users_df)


def update_object(obj, new_obj, username):
    obj_dict = obj.__dict__
    dict_keys = new_obj.keys()
    for dict_key in dict_keys:
        if obj_dict[dict_key] != new_obj[dict_key]:
            query = f"UPDATE public.user SET {dict_key} = '{new_obj[dict_key]}' WHERE username = '{username}';"
            # print(query)
            engine.execute(
                query,
            )
        else:
            pass


def object_to_sql(new_obj):
    dict_keys = new_obj.keys()
    str_t = str(tuple([dict_key for dict_key in dict_keys])).replace("'", "")
    query = f"INSERT INTO public.user {str_t} VALUES{tuple([str(new_obj[dict_key]) for dict_key in dict_keys])};"
    # print(query)
    engine.execute(
        query,
    )


cnt = 0
for indx, ii in users_df.iterrows():
    try:
        username = ii["username"].lower()
    except AttributeError:
        username = ii["username"]
    # print(username)
    is_exists = check_existence(username)
    # print(is_exists)
    if is_exists == True:
        user = db_session.get_user_data_by_username(username)
        update_object(user, ii, username)
    elif is_exists == False:
        object_to_sql(ii)
    print(cnt)
    cnt += 1
