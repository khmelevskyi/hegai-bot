""" bot states for conversation handler """
from enum import Enum


class States(Enum):
    """ states keys """

    MENU = 0

    ADMIN_MENU = 1

    ACCOUNT = 2

    CITY = 3

