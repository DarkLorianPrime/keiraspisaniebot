from sqlalchemy import exists

from vk_base.Models.database import get_database


def query_exists(parameter, parameter_value):
    Session = get_database()
    return Session.query(exists().where(parameter == parameter_value))[0][0]
