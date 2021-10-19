""" conversation handlers of main module """
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler

from .admins import ADMINS
from .db_functions import db_session
from .data import text
from .handlers import start
from .handlers import stop
from .handlers import support_reply
from .handlers import admin
from .handlers import profile
from .handlers import connect_to_admin
from .handlers import push_mssg
from .handlers import check_notion_username
from .handlers import check_username
from .handlers import registration_final
from .handlers import change_name
from .handlers import change_name_save
from .handlers import change_region
from .handlers import change_region_save
from .handlers import change_status
from .handlers import change_status_save
from .handlers import create_region
from .handlers import create_region_save
from .handlers import ask_conv_filters
from .handlers import add_user_tag
from .handlers import find_conversation
# from .handlers import ask_feedback
from .handlers import ask_feedback_result
from .handlers import save_feedback
from .handlers import my_contacts
from .handlers import push_mssg_ask_img
from .handlers import push_mssg_ask_text
from .handlers import push_mssg_final
from .states import States


ADMIN_IDS = [ db_session.get_user_data_by_id(admin_id).chat_id for admin_id in ADMINS ]

admin_filters = Filters.user(ADMIN_IDS) & Filters.chat_type.private

admin_handler = CommandHandler(
    "admin",
    admin,
    filters=admin_filters,
)
necessary_handlers = [
    CommandHandler("start", start, pass_job_queue=True),
    admin_handler,
    CommandHandler("new_region", create_region)
]

support_handler = ConversationHandler(
    name="conversation_support",
    persistent=True,
    entry_points=[
        MessageHandler(Filters.reply, support_reply)
    ],
    states={
        States.SUPPORT_REPLY: [
            *necessary_handlers,
            MessageHandler(Filters.text, support_reply)
        ]
    },
    fallbacks=[CommandHandler("stop", stop)]
)

conv_handler = ConversationHandler(
    name="conversation",
    persistent=True,
    entry_points=necessary_handlers,
    states={
        # -----------------------------------------------------------
        # Profile
        # -----------------------------------------------------------
        States.MENU: [
            *necessary_handlers,
            MessageHandler(Filters.text([text["profile"]]), profile),
            MessageHandler(Filters.text([text["find_conv"]]), ask_conv_filters, pass_job_queue=True),
            MessageHandler(Filters.text([text["my_contacts"]]), my_contacts),
            MessageHandler(Filters.text([text["connect_admin"]]), connect_to_admin),
        ],
        States.ACCOUNT: [
            *necessary_handlers,
            MessageHandler(Filters.text([text["main_menu"]]), start),
            MessageHandler(Filters.text([text["change_name"]]), change_name),
            MessageHandler(Filters.text([text["change_region"]]), change_region),
            MessageHandler(Filters.text([text["change_status"]]), change_status),
        ],
        States.CHANGE_NAME: [
            *necessary_handlers,
            MessageHandler(Filters.text([text["cancel"]]), profile),
            MessageHandler(Filters.text, change_name_save)
        ],
        States.CHANGE_REGION: [
            *necessary_handlers,
            MessageHandler(Filters.text([text["cancel"]]), profile),
            MessageHandler(Filters.text, change_region_save)
        ],
        States.CHANGE_STATUS: [
            *necessary_handlers,
            MessageHandler(Filters.text([text["cancel"]]), profile),
            MessageHandler(Filters.text([text["yes"]]), change_status_save)
        ],
        States.CREATE_REGION: [
            *necessary_handlers,
            MessageHandler(Filters.text([text["cancel"]]), start),
            MessageHandler(Filters.text, create_region_save)
        ],
        States.ADD_USER_TAG: [
            *necessary_handlers,
            MessageHandler(Filters.text([text["cancel"]]), start),
            MessageHandler(Filters.text, add_user_tag)
        ],
        States.FIND_CONVERSATION: [
            *necessary_handlers,
            MessageHandler(Filters.text([text["cancel"]]), start),
            MessageHandler(Filters.text, find_conversation, pass_job_queue=True)
        ],
        States.ASK_FEEDBACK: [
            *necessary_handlers,
            MessageHandler(Filters.text([text["yes"], text["no"]]), ask_feedback_result)
        ],
        States.SAVE_FEEDBACK: [
            *necessary_handlers,
            MessageHandler(Filters.text(["1", "2", "3", "4", "5"]), save_feedback)
        ],
        # -----------------------------------------------------------
        # Registration
        # -----------------------------------------------------------
        States.ASK_USERNAME: [
            *necessary_handlers,
            MessageHandler(Filters.text([text["back"]]), profile),
            MessageHandler(Filters.text, check_notion_username),
        ],
        States.ASK_CONV_OPEN: [
            *necessary_handlers,
            MessageHandler(Filters.text([text["back"]]), check_username),
            MessageHandler(Filters.text([text["yes"], text["no"]]), registration_final)
        ],
        # -----------------------------------------------------------
        # Admin
        # -----------------------------------------------------------
        States.ADMIN_MENU: [
            *necessary_handlers,
            MessageHandler(Filters.text([text["back"]]), start),
            MessageHandler(Filters.text([text["push_mssg"]]), push_mssg),
        ],
        States.PUSH_MSSG_ADD_TEXT: [
            *necessary_handlers,
            MessageHandler(Filters.text([text["cancel"]]), admin),
            MessageHandler(Filters.text, push_mssg_ask_text),
        ],
        States.PUSH_MSSG_ADD_IMG: [
            *necessary_handlers,
            MessageHandler(Filters.text([text["cancel"]]), admin),
            MessageHandler(Filters.text, push_mssg_ask_img),
        ],
        States.PUSH_MSSG_FINAL: [
            *necessary_handlers,
            MessageHandler(Filters.text([text["cancel"]]), admin),
            MessageHandler(Filters.text, push_mssg_final),
            MessageHandler(Filters.photo, push_mssg_final),
        ],
    },
    fallbacks=[CommandHandler("stop", stop)],
)
