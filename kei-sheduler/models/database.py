import os

from sqlalchemy import create_engine, exists
import dotenv
from sqlalchemy.orm import sessionmaker


def get_database():
    dotenv.load_dotenv()
    connect_url = f'postgresql://{os.getenv("user")}:{os.getenv("password")}@{os.getenv("host")}/{os.getenv("name")}'
    engine = create_engine(connect_url)
    Session = sessionmaker(bind=engine, autocommit=True)
    return Session()


def query_exists(parameter, parameter_value):
    Session = get_database()
    return Session.query(exists().where(parameter == parameter_value))[0][0]


session = get_database()
