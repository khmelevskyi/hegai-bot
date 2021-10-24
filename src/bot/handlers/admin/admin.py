""" basic single functions and admin menu """
from telegram import ParseMode
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram import Update
from telegram.ext import CallbackContext

from ...hegai_db import Permission
from ...db_functions import db_session
from ...admins import ADMINS
from ...data import text
from ...states import States


def admin_keyboard_markup() -> ReplyKeyboardMarkup:
    """ returns admin keyboard layout """

    admin_keyboard = [
        [text["push_mssg"]],
        [text["stats"]],
        [text["back"]],
    ]
    markup = ReplyKeyboardMarkup(keyboard=admin_keyboard, resize_keyboard=True)
    return markup


def admin(update: Update, context: CallbackContext):
    """ welcomes admin """
    chat_id = update.message.chat.id
    # university_id = db_session.get_user_data(chat_id=chat_id)[0]
    university = "uni" # cached_data.list_universities()[university_id][0]
    context.bot.send_message(
        chat_id=chat_id,
        text=text["hi_admin"], # ADMINS[chat_id][0]
        reply_markup=admin_keyboard_markup(),
        parse_mode=ParseMode.HTML,
    )
    return States.ADMIN_MENU

def push_mssg(update: Update, context: CallbackContext):
    """ asks wether to send a mssg to moscow ppl, all ppl """

    chat_id = update.message.chat.id

    reply_keyboard = [
        ["Только москвичи"],
        ["Все"],
        [text["cancel"]],
    ]
    markup = ReplyKeyboardMarkup(keyboard=reply_keyboard, resize_keyboard=True)

    context.bot.send_message(
        chat_id=chat_id,
        text="Выберите кому отправить сообщение:",
        reply_markup=markup,
        parse_mode=ParseMode.HTML,
    )
    return States.PUSH_MSSG_ADD_TEXT

def push_mssg_ask_text(update: Update, context: CallbackContext):
    """ asks wether to send a mssg to moscow ppl, all ppl """

    chat_id = update.message.chat.id
    mssg = update.message.text
    context.user_data["push_address"] = mssg

    reply_keyboard = [
        [text["cancel"]],
    ]
    markup = ReplyKeyboardMarkup(keyboard=reply_keyboard, resize_keyboard=True)

    context.bot.send_message(
        chat_id=chat_id,
        text="Напишите текст сообщения:",
        reply_markup=markup,
        parse_mode=ParseMode.HTML,
    )
    return States.PUSH_MSSG_ADD_IMG

def push_mssg_ask_img(update: Update, context: CallbackContext):
    """ asks wether to send a mssg to moscow ppl, all ppl """

    chat_id = update.message.chat.id
    mssg = update.message.text
    context.user_data["push_text"] = mssg

    reply_keyboard = [
        [text["skip"]],
        [text["cancel"]]
    ]
    markup = ReplyKeyboardMarkup(keyboard=reply_keyboard, resize_keyboard=True)

    context.bot.send_message(
        chat_id=chat_id,
        text="Добавьте фотографию:",
        reply_markup=markup,
        parse_mode=ParseMode.HTML,
    )
    return States.PUSH_MSSG_FINAL

def push_mssg_final(update: Update, context: CallbackContext):
    """ pass """

    img = update.message.photo
    print(img)
    push_text = context.user_data.pop("push_text")
    push_address = context.user_data.pop("push_address")

    if push_address == "Только москвичи":
        users = db_session.get_all_users_by_region("Москва")
        users += db_session.get_all_users_by_region("Moscow")
    else:
        users = db_session.get_all_users()

    for user in users:
        print(user)
        chat_id = user.chat_id
        if chat_id == None:
            continue

        if img == []:
            context.bot.send_message(
                chat_id=chat_id,
                text=push_text,
                parse_mode=ParseMode.HTML
            )
        else:
            context.bot.send_photo(
                chat_id=chat_id,
                photo=img[0],
                caption=push_text,
                parse_mode=ParseMode.HTML
            )

    return admin(update, context)


def drop_user(update: Update, context: CallbackContext):
    """ drop user from all tables in db """

    msg = update.message.text
    split_msg = msg.split(" ")
    if len(split_msg) == 1:
        context.bot.send_message(
            chat_id=update.message.chat.id,
            text="id not provided, use it like:\n\n/drop 1488228",
        )
    else:
        chat_id = int(split_msg[-1])
        error, db_msg = db_session.drop_user_cascade(chat_id)
        if not error:
            context.bot.send_message(
                chat_id=chat_id,
                text=text["user_deleted"],
            )
        full_msg = f"Error: {error}\n\n{db_msg}"
        context.bot.send_message(
            chat_id=update.message.chat.id,
            text=full_msg,
        )


def set_user(update: Update, context: CallbackContext):
    """ set uni_id and user data to admin account """

    msg = update.message.text
    split_msg = msg.split(" ")
    if len(split_msg) == 1:
        context.bot.send_message(
            chat_id=update.message.chat.id,
            text="id not provided, use it like:\n\n/set 1488228",
        )
    else:
        admin_id = update.message.chat.id
        chat_id = int(split_msg[-1])
        error, db_msg = db_session.set_user(admin_id, chat_id)
        full_msg = f"Error: {error}\n\n{db_msg}"
        context.bot.send_message(
            chat_id=update.message.chat.id,
            text=full_msg,
        )


def everyday_news(*args):
    """ collects and sends general data analitics """
    statistics = db_session.get_statistics()

    news_msg = (
        "За день | неделю | месяц:\n\n"
        + "<b>Новых  пользователей</b>\n"
        + "• {} | {} | {}\n\n".format(*statistics["new_users"])
        + "<b>Новых действий</b>\n"
        + "• {} | {} | {}\n\n".format(*statistics["actions"])
        + "<b>Активных  пользователей</b>\n"
        + "• {} | {} | {}\n\n".format(*statistics["active_users"])
        + "\nВсего {} пользователей:\n".format(statistics["total_users"][0])
    )

    admin_ids = ADMINS

    if len(args) == 1:  # depends if it called by job_queue or updater
        context = args[0]

        for admin_id in admin_ids:
            user_chat_id = db_session.get_user_data_by_id(admin_id).chat_id
            context.bot.send_message(chat_id=user_chat_id, text=news_msg)
    else:
        update, context = args[0], args[1]

        admin_ids = [update.message.chat.id]

        for admin_id in admin_ids:
            context.bot.send_message(chat_id=admin_id, text=news_msg)


