import pandas as pd
from bot.db_functions import db_session
from sqlalchemy import create_engine
from sqlalchemy.types import BigInteger
from sqlalchemy.types import Integer
from sqlalchemy.types import VARCHAR

users_df = pd.read_csv(
    "initial_data_formation/users.csv",
    usecols=["id", "telegram_chat_id", "username", "full_name", "city"],
)

users_df = users_df.rename(
    columns={"id": "notion_id", "telegram_chat_id": "chat_id", "city": "region"}
)

users_df = users_df.dropna(subset=["chat_id"])

regions = users_df["region"].tolist()
regions_dict = {}
for region in regions:
    if isinstance(region, float):
        region = None
    try:
        region_id = db_session.get_region_by_name(region).id
    except AttributeError:
        region_id = None
    regions_dict[region] = region_id

users_df["region"].replace(regions_dict, inplace=True)
print(users_df)


engine = create_engine("postgresql://postgres:dsfdfe34@localhost:5432/hegai-bot")


users_df.to_sql(
    "user",
    engine,
    dtype={
        "chat_id": BigInteger(),
        "notion_id": VARCHAR(),
        "full_name": VARCHAR(),
        "username": VARCHAR(),
        "region": Integer(),
    },
    index=False,
    if_exists="append",
)
