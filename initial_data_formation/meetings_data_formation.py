import pandas as pd
from bot.db_functions import db_session
from sqlalchemy import create_engine

engine = create_engine("postgresql://postgres:dsfdfe34@localhost:5432/hegai-bot")

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
    # print(is_exists)
    if is_exists == True:
        is_exists = check_existence(user_two)
        if is_exists == True:
            user_one = db_session.get_user_data_by_notion_id(user_one)
            user_two = db_session.get_user_data_by_notion_id(user_two)
            db_session.add_contacts(user_one.id, user_two.id)
