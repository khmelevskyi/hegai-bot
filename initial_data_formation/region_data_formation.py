import pandas as pd


from sqlalchemy import create_engine
from sqlalchemy.types import VARCHAR

region_df = pd.read_csv("initial_data_formation/users.csv", usecols=["city"])

engine = create_engine('postgresql://postgres:dsfdfe34@localhost:5432/hegai-bot')

region_df = region_df.rename(columns={
    "city": "name"
})

users_df = region_df.dropna(subset=['name'])
region_df = region_df.groupby("name").sum().reset_index()

region_df = region_df[~region_df["name"].str.contains('/')]
region_df = region_df[~region_df["name"].str.contains(',')]
region_df = region_df[~region_df["name"].str.contains(' и ')]
region_df = region_df[~region_df["name"].str.contains(' or ')]
region_df = region_df[~region_df["name"].str.contains('Поехали 🚀')]
region_df = region_df[~region_df["name"].str.contains('Ок')]
region_df = region_df[~region_df["name"].str.contains('Николай Гришин')]
region_df = region_df[~region_df["name"].str.contains('Москве')]
region_df = region_df[~region_df["name"].str.contains('Моосква')]
region_df = region_df[~region_df["name"].str.contains('MOSCOW')]
region_df = region_df[~region_df["name"].str.contains('Москва-Махачкала')]
region_df = region_df[~region_df["name"].str.contains('sdf')]
region_df = region_df[~region_df["name"].str.contains('Espoo')]
region_df = region_df[~region_df["name"].str.contains('Москва-Иркутск-Красноярск')]
region_df = region_df[~region_df["name"].str.contains('Сан Франциско')]
region_df = region_df[~region_df["name"].str.contains('Сан-франциско')]
region_df = region_df[~region_df["name"].str.contains('Санкт Петербург')]
region_df = region_df[~region_df["name"].str.contains('Петербург')]
region_df = region_df[~region_df["name"].str.contains('бали')]
region_df = region_df[~region_df["name"].str.contains('москва')]
region_df = region_df[~region_df["name"].str.contains('сеул')]
region_df = region_df[~region_df["name"].str.contains('Kiev')]
region_df = region_df[~region_df["name"].str.contains('Татьяна')]
region_df = region_df[~region_df["name"].str.contains('Улан-удэ')]
region_df = region_df[region_df["name"].str.len() > 1]

print(region_df)

region_df.to_sql('region', engine, dtype={"region": VARCHAR()}, index=False, if_exists="append")
