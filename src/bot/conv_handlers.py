""" conversation handlers of main module """
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler

# from .admins import ADMINS
from .data import text
from .handlers import start
from .handlers import stop
from .handlers import admin
from .handlers import profile
from .handlers import check_notion_username
from .handlers import check_username
from .handlers import registration_final
from .states import States


# ADMIN_IDS = list(ADMINS.keys())

# admin_filters = Filters.user(ADMIN_IDS) & Filters.chat_type.private

# admin_handler = CommandHandler(
#     "admin",
#     admin,
#     filters=admin_filters,
# )
necessary_handlers = [
    CommandHandler("start", start),
    # admin_handler,
]

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
            MessageHandler(Filters.text([text["admin_menu"]]), admin),
            MessageHandler(Filters.text([text["profile"]]), profile),
        ],
        States.ACCOUNT: [
            *necessary_handlers,
            MessageHandler(Filters.text([text["main_menu"]]), start),
            # MessageHandler(Filters.text([text["change_name"]]), change_name),
            # MessageHandler(Filters.text([text["change_region"]]), change_region),
            # MessageHandler(Filters.text([text["change_status"]]), change_status),
        ],
        # -----------------------------------------------------------
        # Registration
        # -----------------------------------------------------------
        States.ASK_USERNAME: [
            MessageHandler(Filters.text([text["back"]]), profile),
            MessageHandler(Filters.text, check_notion_username),
        ],
        States.ASK_CONV_OPEN: [
            MessageHandler(Filters.text([text["back"]]), check_username),
            MessageHandler(Filters.text([text["yes"], text["no"]]), registration_final)
        ]
        # -----------------------------------------------------------
        # Admin
        # -----------------------------------------------------------
        # States.CITY: [
        #     MessageHandler(Filters.text([text["back"]]), profile),
        #     MessageHandler(Filters.text, ask_university),
        # ],
    },
    fallbacks=[CommandHandler("stop", stop)],
)
