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
        # States.ACCOUNT: [
        #     *necessary_handlers,
        #     MessageHandler(Filters.text([text["admin_menu"]]), admin),
        #     MessageHandler(Filters.text([text["change_button"]]), ask_region),
        #     MessageHandler(Filters.text([text["back"]]), start),
        # ],
        # -----------------------------------------------------------
        # Registration
        # -----------------------------------------------------------
        # States.CITY: [
        #     MessageHandler(Filters.text([text["back"]]), profile),
        #     MessageHandler(Filters.text, ask_university),
        # ],
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
