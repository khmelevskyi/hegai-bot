# import os
# import pprint
import pandas as pd
# from tabulate import tabulate


from sqlalchemy import create_engine
from sqlalchemy.types import Integer, BigInteger, CHAR, VARCHAR

users_df = pd.read_csv("paches/users.csv", usecols=["id", "telegram_chat_id", "username", "full_name"])

users_df.to_csv("paches/new_users.csv")

users_df = users_df.rename(columns={
    "id": "notion_id", 
    "telegram_chat_id": "chat_id",
})

users_df = users_df.dropna(subset=['chat_id'])

# users_df = users_df.fillna(0)
# users_df = users_df.astype({"chat_id": int})

engine = create_engine('postgresql://postgres:dsfdfe34@localhost:5432/hegai-bot')


users_df.to_sql('user', engine, dtype={"chat_id": BigInteger(), "notion_id": VARCHAR(), "full_name": VARCHAR(), "username": VARCHAR()}, index=False) # if_exists="append"