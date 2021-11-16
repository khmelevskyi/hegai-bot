""" bot states for conversation handler """
from enum import Enum


class States(Enum):
    """ states keys """

    MENU = 0

    ADMIN_MENU = 1

    ACCOUNT = 2

    ASK_USERNAME = 3

    ASK_CONV_OPEN = 4

    CHANGE_STATUS = 7

    DEFAULT_TAGS_OR_NEW = 8

    FIND_CONVERSATION = 9

    ASK_FEEDBACK = 10

    SAVE_FEEDBACK = 11

    ADD_USER_TAG = 12

    PUSH_MSSG_ADD_TEXT = 13

    PUSH_MSSG_ADD_IMG = 14

    PUSH_MSSG_FINAL = 15

    SUPPORT_REPLY = 16

    PUSH = 17

    EXISTING_REQUEST = 18

    CHOOSING_TAGS = 20

    CHANGE_CHOOSING_TAGS = 21

    MANUAL_MATCH = 22
