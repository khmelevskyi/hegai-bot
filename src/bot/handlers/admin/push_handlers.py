""" send push notifications to all users """
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import ParseMode
from telegram import ReplyKeyboardMarkup
from telegram import Update
from telegram.ext import CallbackContext

from ...data import text
from .admin import admin
from .push_message import PushMessage
from ..broadcast import run_broadcast
from ...states import States
from ...utils import generate_markup
from ...utils import restricted
from ...utils import send_msg
from ...utils import send_typing_action
from ...db_functions import db_session


push_message = PushMessage()

inline_delete = InlineKeyboardButton(
    text["delete_inline_btn"], callback_data="delete_url_button"
)
inline_add = InlineKeyboardButton(
    text["add_inline_btn"], callback_data="add_url_button"
)
inline_back = InlineKeyboardButton(text["back"], callback_data="back_to_push")


@restricted(None)
def ask_push_text(update: Update, context: CallbackContext):
    """ ask user to give push msg """
    mssg = update.message.text
    context.user_data["push_address"] = mssg

    push_message.flush()  # clear from prevoius time
    send_msg(update, text["ask_push_text"], markup=generate_markup())
    return States.PUSH


@restricted(None)
def display_push(update: Update, context: CallbackContext):
    """ retrives push msg and veryfies sending """

    if not push_message.message:
        # record msg if it's empty
        push_message.message = update.message
    message = push_message.message

    if push_message.button:
        keyboard = [[push_message.button], [inline_delete]]
    else:
        keyboard = [[inline_add]]
    inline_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        # from back to push inline button
        update.callback_query.answer()

        update = update.callback_query
        # return properties of push msg
        if update.message.photo:
            update.edit_message_caption(
                caption=message.caption_html, parse_mode=ParseMode.HTML
            )
        else:
            update.edit_message_text(text=message.text_html, parse_mode=ParseMode.HTML)
        update.edit_message_reply_markup(reply_markup=inline_markup)
    else:
        # direct call to print push msg
        reply_keyboard = [[text["drop_mailing"], text["start_mailing"]]]
        update.message.reply_text(
            text="Пользователи получат такое сообщение:",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True),
        )
        if message.photo:
            update.message.reply_photo(
                message.photo[-1],
                reply_markup=inline_markup,
                caption=message.caption_html,
            )
        else:
            update.message.reply_text(
                text=message.text_html,
                reply_markup=inline_markup,
                disable_web_page_preview=True,
            )

    return States.PUSH


@restricted(None)
def ask_url_button(update: Update, context: CallbackContext):
    """ ask for url button """

    if update.callback_query:
        update.callback_query.answer()

        update = update.callback_query
        if update.message.photo:  # turn push text into question
            update.edit_message_caption(caption=text["ask_url_button"])
        else:
            update.edit_message_text(text=text["ask_url_button"])

        markup = InlineKeyboardMarkup([[inline_back]], resize_keyboard=True)
        update.edit_message_reply_markup(reply_markup=markup)
    return States.PUSH


@restricted(None)
def set_url_button(update: Update, context: CallbackContext):
    """ create url button for push msg """

    msg = update.message.text.split("~")
    if len(msg) == 2:
        push_message.button = tuple(map(lambda x: x.strip(), msg))
        return display_push(update, context)
    update.message.reply_text("Wrong input format")
    return ask_url_button(update, context)


@restricted(None)
def delete_url_button(update: Update, context: CallbackContext):
    """ remove url button from push msg """

    if update.callback_query:
        update.callback_query.answer()
    del push_message.button
    return display_push(update, context)


@restricted(None)
@send_typing_action
def prepare_broadcast(update: Update, context: CallbackContext):
    """ send push msg to all users """

    broadcast_func = push_message.get_broadcast_func(context)
    push_kwargs = push_message.kwargs

    push_address = context.user_data["push_address"]
    if push_address == text["push_moscow"]:
        users = db_session.get_all_users_for_broadcast_by_region("Москва")
        users += db_session.get_all_users_for_broadcast_by_region("Moscow")
    elif push_address == text["push_all"]:
        users = db_session.get_all_users_for_broadcast()

    # users = [  # debug ids
    #     (476800499, False),
    #     (989397887, False),
    #     (-1001476067038, True),
    # ]
    context.dispatcher.run_async(
        run_broadcast,
        broadcast_func,
        users,
        push_kwargs,
        {},
        update,
    )
    return admin(update, context)
