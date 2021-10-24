""" db base file"""
# import db_models as m
import sys
from os import getenv
from os import path

from colorama import Fore
from colorama import init
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

init(autoreset=True)


# from progressbar import progressbar


load_dotenv()

# base_dir = path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
# sqlite_dir = path.join(base_dir, "new.sqlite")
# sqlite_db = {"drivername": "sqlite", "database": sqlite_dir}
# sqlite_uri = URL(**sqlite_db)
# sqlite_engine = create_engine(sqlite_uri)
# sq_session = sessionmaker(bind=sqlite_engine)


postgres_db = {
    "drivername": "postgresql",
    "username": getenv("DB_USERNAME"),
    "password": getenv("DB_PASSWORD"),
    "host": getenv("DB_HOST"),
    "port": int(getenv("DB_PORT", 5432)),
    "database": getenv("DB_DATABASE"),
}
postgres_uri = URL(**postgres_db)
db_uri = postgres_uri  # passed to alembic

postgres_engine = create_engine(
    postgres_uri,
    pool_size=10,
    max_overflow=2,
    pool_recycle=300,
    pool_pre_ping=True,
    pool_use_lifo=True,
    # echo=True
)

pg_session = sessionmaker(bind=postgres_engine)

Session = scoped_session(pg_session)


def testdb():
    """ run empty transaction """

    try:
        Session().execute("SELECT 1 WHERE false;")
        print(Fore.GREEN + "-------- DB conn test Successful --------")
    except:
        print(Fore.RED + "!!!!!!!! DB conn test Failed !!!!!!!!")


testdb()


# print("\nDB_URI: ", db_uri, "\n")

# echo_value = "-db" in sys.argv
# print("-" * 6, "SQLalchemy logging is " + str(echo_value), "-" * 6, "\n")

# m.Base.metadata.create_all(postgres_engine)
