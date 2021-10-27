import os
from dotenv import load_dotenv
import pandas as pd
from bot.db_functions import db_session
from sqlalchemy import create_engine

load_dotenv()

db_username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
database = os.getenv("DB_DATABASE")

engine = create_engine(
    f"postgresql://{db_username}:{password}@{host}:{port}/{database}"
)

users_df = pd.read_csv(
    "initial_data_formation/meetings.csv", usecols=["user_id", "partner_id"]
)

users_df = users_df.rename(
    columns={
        "user_id": "user_one",
        "partner_id": "user_two",
    }
)


def check_existence(notion_id):
    query = "SELECT EXISTS (SELECT 1 FROM public.user WHERE notion_id = %s);"
    return list(engine.execute(query, (notion_id,)))[0][0] == 1


for indx, ii in users_df.iterrows():
    user_one = ii["user_one"]
    user_two = ii["user_two"]
    is_exists = check_existence(user_one)
    print(is_exists)
    if is_exists == True:
        is_exists = check_existence(user_two)
        if is_exists == True:
            user_one = db_session.get_user_data_by_notion_id(user_one)
            user_two = db_session.get_user_data_by_notion_id(user_two)
            db_session.add_contacts(user_one.id, user_two.id)
