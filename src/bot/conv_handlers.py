""" conversation handlers of main module """
from telegram.ext import CallbackQueryHandler
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler

from .data import text
from .data import URL_BUTTON_REGEX
from .db_functions import db_session
from .handlers import add_user_tag
from .handlers import admin
from .handlers import default_or_choose
from .handlers import ask_conv_filters
from .handlers import next_back_page_tags
from .handlers import prev_next_category_tags
from .handlers import create_conv_request
from .handlers import ask_feedback_result
from .handlers import change_status
from .handlers import change_status_save
from .handlers import check_notion_username
from .handlers import check_username
from .handlers import connect_to_admin
from .handlers import find_conversation
from .handlers import cancel_request
from .handlers import my_contacts
from .handlers import profile
from .handlers import push_mssg

# from .handlers import push_mssg_ask_img
# from .handlers import push_mssg_ask_text
# from .handlers import push_mssg_final
from .handlers import registration_final
from .handlers import save_feedback
from .handlers import start_init
from .handlers import start
from .handlers import stop
from .handlers import help
from .handlers import bot_faq
from .handlers import support_reply
from .handlers import ask_push_text
from .handlers import display_push
from .handlers import ask_url_button
from .handlers import set_url_button
from .handlers import delete_url_button
from .handlers import prepare_broadcast
from .handlers import broadcast_status
from .handlers import bot_statistics
from .handlers import ask_users_to_match
from .handlers import manual_match
from .states import States


ADMIN_IDS = [
    db_session.get_user_data_by_id(admin_id).chat_id
    for admin_id in db_session.get_admins()
]

admin_filters = Filters.user(ADMIN_IDS) & Filters.chat_type.private

admin_handler = CommandHandler(
    "admin",
    admin,
    filters=admin_filters,
)


push_status_handler = CommandHandler(
    "push_status", broadcast_status, filters=admin_filters
)


necessary_handlers = [
    CommandHandler("start", start_init, pass_job_queue=True),
    CommandHandler("help", help),
    admin_handler,
    CallbackQueryHandler(
        ask_feedback_result,
        pass_chat_data=True,
        pass_user_data=True,
        pass_update_queue=True,
        pattern="^feedback",
    ),
]

support_handler = ConversationHandler(
    name="conversation_support",
    persistent=True,
    entry_points=[MessageHandler(Filters.reply, support_reply)],
    states={
        States.SUPPORT_REPLY: [
            *necessary_handlers,
            MessageHandler(Filters.text, support_reply),
        ]
    },
    fallbacks=[CommandHandler("stop", stop)],
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
            MessageHandler(Filters.text([text["find_conv"]]), default_or_choose),
            MessageHandler(Filters.text([text["my_contacts"]]), my_contacts),
            MessageHandler(Filters.text([text["connect_admin"]]), connect_to_admin),
            MessageHandler(Filters.text([text["bot_faq"]]), bot_faq),
        ],
        States.ACCOUNT: [
            *necessary_handlers,
            MessageHandler(Filters.text([text["main_menu"]]), start),
            MessageHandler(Filters.text([text["change_status"]]), change_status),
        ],
        States.CHANGE_STATUS: [
            *necessary_handlers,
            MessageHandler(Filters.text([text["cancel"]]), profile),
            MessageHandler(Filters.text([text["yes"]]), change_status_save),
        ],
        States.ADD_USER_TAG: [
            *necessary_handlers,
            MessageHandler(Filters.text([text["cancel"]]), start),
            MessageHandler(Filters.text, add_user_tag),
        ],
        States.DEFAULT_TAGS_OR_NEW: [
            *necessary_handlers,
            MessageHandler(Filters.text([text["back"]]), start),
            MessageHandler(
                Filters.text([text["use_profile_tags"], text["choose_tags_yourself"]]),
                ask_conv_filters,
            ),
        ],
        States.FIND_CONVERSATION: [
            *necessary_handlers,
            MessageHandler(Filters.text([text["back"]]), start),
            MessageHandler(Filters.text([text["cancel"]]), start),
            MessageHandler(Filters.text, find_conversation, pass_job_queue=True),
        ],
        States.EXISTING_REQUEST: [
            *necessary_handlers,
            MessageHandler(Filters.text([text["ok"]]), start),
            MessageHandler(Filters.text([text["cancel_request"]]), cancel_request),
        ],
        States.SAVE_FEEDBACK: [
            *necessary_handlers,
            MessageHandler(Filters.text, save_feedback),
        ],
        States.CHOOSING_TAGS: [
            MessageHandler(Filters.text([text["cancel"]]), start),
            CallbackQueryHandler(add_user_tag, pattern="^tag-"),
            CallbackQueryHandler(next_back_page_tags, pattern="next"),
            CallbackQueryHandler(next_back_page_tags, pattern="back"),
            CallbackQueryHandler(start, pattern="cancel"),
            CallbackQueryHandler(prev_next_category_tags, pattern="category_n"),
            CallbackQueryHandler(prev_next_category_tags, pattern="category_p"),
            CallbackQueryHandler(create_conv_request, pattern="finish_t"),
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
            MessageHandler(Filters.text([text["yes"], text["no"]]), registration_final),
        ],
        # -----------------------------------------------------------
        # Admin
        # -----------------------------------------------------------
        States.ADMIN_MENU: [
            *necessary_handlers,
            MessageHandler(Filters.text([text["back"]]), start),
            MessageHandler(Filters.text([text["stats"]]), bot_statistics),
            MessageHandler(Filters.text([text["mailing"]]), push_mssg),
            MessageHandler(Filters.text([text["manual_match"]]), ask_users_to_match),
            # MessageHandler(Filters.text([text["push_mssg"]]), push_mssg),
        ],
        States.PUSH_MSSG_ADD_TEXT: [
            *necessary_handlers,
            MessageHandler(Filters.text([text["cancel"]]), admin),
            MessageHandler(Filters.text, ask_push_text),
        ],
        # States.PUSH_MSSG_ADD_IMG: [
        #     *necessary_handlers,
        #     MessageHandler(Filters.text([text["cancel"]]), admin),
        #     MessageHandler(Filters.text, push_mssg_ask_img),
        # ],
        # States.PUSH_MSSG_FINAL: [
        #     *necessary_handlers,
        #     MessageHandler(Filters.text([text["cancel"]]), admin),
        #     MessageHandler(Filters.text, push_mssg_final),
        #     MessageHandler(Filters.photo, push_mssg_final),
        # ],
        States.PUSH: [
            MessageHandler(Filters.text([text["back"]]), admin),
            MessageHandler(Filters.text([text["drop_mailing"]]), admin),
            CallbackQueryHandler(ask_url_button, pattern="add_url_button"),
            CallbackQueryHandler(delete_url_button, pattern="delete_url_button"),
            CallbackQueryHandler(display_push, pattern="back_to_push"),
            MessageHandler(Filters.text([text["start_mailing"]]), prepare_broadcast),
            MessageHandler(Filters.regex(URL_BUTTON_REGEX), set_url_button),
            MessageHandler((Filters.text | Filters.photo), display_push),
        ],
        States.MANUAL_MATCH: [
            MessageHandler(Filters.text([text["back"]]), admin),
            MessageHandler(Filters.text, manual_match),
        ],
    },
    fallbacks=[CommandHandler("stop", stop)],
)
