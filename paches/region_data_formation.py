# import os
# import pprint
import re
import pandas as pd
# from tabulate import tabulate


from sqlalchemy import create_engine
from sqlalchemy.types import Integer, BigInteger, CHAR, VARCHAR

region_df = pd.read_csv("paches/users.csv", usecols=["city"])

engine = create_engine('postgresql://postgres:dsfdfe34@localhost:5432/hegai-bot')

region_df = region_df.rename(columns={
    "city": "name"
})

region_df = region_df.groupby("name").sum().reset_index()

region_df = region_df[~region_df["name"].str.contains('/')]
region_df = region_df[~region_df["name"].str.contains(',')]
region_df = region_df[region_df["name"].str.len() > 1]
# print(region_df)

region_df.to_sql('region', engine, dtype={"region": VARCHAR()}, index=False, if_exists="append")

###
# users_df = pd.read_csv("paches/users.csv", usecols=["telegram_chat_id", "city"])

# users_df.to_csv("paches/new_users.csv")

# users_df = users_df.rename(columns={
#     "telegram_chat_id": "chat_id",
#     "city": "region"
# })

# users_df = users_df.dropna(subset=['chat_id'])

# # users_df = users_df.fillna(0)
# # users_df = users_df.astype({"chat_id": int})

# engine = create_engine('postgresql://postgres:dsfdfe34@localhost:5432/hegai-bot')


# users_df.to_sql('user', engine, dtype={"chat_id": BigInteger(), "region": VARCHAR()}, index_label="chat_id", if_exists="append")