""" separete file to avoid circular import during db import """
from ..db_functions import db_session


ADMINS = db_session.get_admins()
