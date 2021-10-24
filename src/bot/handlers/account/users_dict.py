""" user data cache on registration process """
from typing import Any
from typing import Dict


# dictionary gathers user data before inserting it to the database
# users key is a chat_id
users: Dict[int, Any] = dict()
