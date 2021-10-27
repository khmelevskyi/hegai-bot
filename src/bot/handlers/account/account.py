""" basic info abount user and registrarion process for student and teacher """
from telegram import ParseMode
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import Update
from telegram.ext import CallbackContext

from ...data import start_keyboard
from ...data import text
from ...db_functions import db_session
from ...states import States
from .utils import users

# from ...db_functions import Action


def profile(update: Update, context: CallbackContext):
    """ basic account info """

    chat_id = update.message.chat.id

    if chat_id in users:  # if user returned from registration form
        users.pop(chat_id, None)

    user = db_session.get_user_data(chat_id)

    # db_session.log_action(chat_id=chat_id, action=Action.profile)

    if user.notion_id is None:
        context.bot.send_message(
            chat_id=update.message.chat.id, text=text["not_registered"]
        )
        return States.MENU

    conv_open = user.conversation_open
    if conv_open is True:
        conv_open = "Открыт к разговору"
    else:
        conv_open = "Не открыт к разговору"

    if user.region != None:
        region_name = db_session.get_region(user.region).name
    else:
        region_name = "Не указан"

    user_tags = db_session.get_user_tags(chat_id)
    user_tags_names = []
    for user_tag in user_tags:
        tag_name = db_session.get_tag(user_tag.tag_id).name
        user_tags_names.append(tag_name)

    user_tags_names_str = str(user_tags_names)
    user_tags_names = (
        user_tags_names_str.replace("'", "").replace("[", "").replace("]", "")
    )

    div = 30
    info = (
        f"<i>{user.full_name}</i>\n"
        + f"{text['account_n']} @{user.username}\n"
        + f"Регион: {region_name}\n"
        + f"<i>id </i>: {chat_id}\n"
        # + f"<i>notion id </i>: {user.notion_id}\n"
        + "-" * div
        + f"\nСтатус: <b>{conv_open}</b>\n"
        + f"\nТеги: {user_tags_names}\n"
        # + f"\nС нами с: {user.time_registered}\n"
        + "~" * (div // 2)
        + "\n"
        + text["more_info"]
    )

    reply_keyboard = [
        [text["change_name"], text["change_region"]],
        [text["change_status"], text["change_tags"]],
        [text["main_menu"]],
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, selective=True)

    context.bot.send_message(
        chat_id=chat_id,
        text=info,
        reply_markup=markup,
        parse_mode=ParseMode.HTML,
    )
    return States.ACCOUNT


### change name
def change_name(update: Update, context: CallbackContext):
    """ edits user's name """

    chat_id = update.message.chat.id

    reply_keyboard = [
        [text["cancel"]],
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, selective=True)

    context.bot.send_message(
        chat_id=chat_id, text="Enter your new name:", reply_markup=markup
    )

    return States.CHANGE_NAME


def change_name_save(update: Update, context: CallbackContext):
    """ saves new user's name """

    chat_id = update.message.chat.id
    mssg = update.message.text

    context.bot.send_message(
        chat_id=chat_id, text=text["edit_success"], reply_markup=ReplyKeyboardRemove()
    )

    db_session.save_new_name(chat_id, mssg)

    return profile(update, context)


### change region
def change_region(update: Update, context: CallbackContext):
    """ edits user's region """

    chat_id = update.message.chat.id

    regions = db_session.get_all_regions()

    reply_keyboard = []
    for region in regions:
        reply_keyboard.append([region.name])
    reply_keyboard.append([text["cancel"]])

    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, selective=True)

    context.bot.send_message(
        chat_id=chat_id, text="Choose a new region:", reply_markup=markup
    )

    return States.CHANGE_REGION


def change_region_save(update: Update, context: CallbackContext):
    """ saves new user's region """

    chat_id = update.message.chat.id
    mssg = update.message.text

    regions = db_session.get_all_regions()
    for region in regions:
        if region.name == mssg:
            region_id = region.id

    context.bot.send_message(
        chat_id=chat_id, text=text["edit_success"], reply_markup=ReplyKeyboardRemove()
    )

    db_session.save_new_region(chat_id, region_id)

    return profile(update, context)


### change status
def change_status(update: Update, context: CallbackContext):
    """ edits user's status """

    chat_id = update.message.chat.id

    user = db_session.get_user_data(chat_id)

    if user.conversation_open is True:
        status_text = "Не открыт к разговору"
    else:
        status_text = "Открыт к разговору"

    reply_keyboard = [
        [text["yes"]],
        [text["cancel"]],
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, selective=True)

    context.bot.send_message(
        chat_id=chat_id,
        text=f"Chnage status to: <b>{status_text}</b>",
        reply_markup=markup,
        parse_mode=ParseMode.HTML,
    )

    return States.CHANGE_STATUS


def change_status_save(update: Update, context: CallbackContext):
    """ saves new user's status """

    chat_id = update.message.chat.id

    context.bot.send_message(
        chat_id=chat_id, text=text["edit_success"], reply_markup=ReplyKeyboardRemove()
    )

    db_session.save_new_status(chat_id)

    return profile(update, context)


def create_region(update: Update, context: CallbackContext):
    """ creates a new region """

    chat_id = update.message.chat.id

    reply_keyboard = [[text["cancel"]]]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, selective=True)

    context.bot.send_message(
        chat_id=chat_id, text="Enter a region name", reply_markup=markup
    )

    return States.CREATE_REGION


def start_markup() -> ReplyKeyboardMarkup:
    """ markup for start keyboard """
    markup = ReplyKeyboardMarkup(
        keyboard=start_keyboard, resize_keyboard=True, selective=True
    )
    return markup


def create_region_save(update: Update, context: CallbackContext):
    """ saves a new region """

    chat_id = update.message.chat.id
    mssg = update.message.text

    db_session.create_region(mssg)

    context.bot.send_message(
        chat_id=chat_id,
        text="Region created successfully!",
        reply_markup=ReplyKeyboardRemove(),
    )

    context.bot.send_message(
        chat_id=update.message.chat.id, text=text["start"], reply_markup=start_markup()
    )

    return States.MENU


### change tags
def change_user_tags(update: Update, context: CallbackContext):
    """ asks user for filters for finding a conversation """

    chat_id = update.message.chat.id

    user_tags = db_session.get_user_tags(chat_id)
    if len(user_tags) > 0:
        user_tags = db_session.get_user_tags(chat_id)
        for user_tag in user_tags:
            user_tag_id = user_tag.id
            db_session.remove_user_tag(user_tag_id)

    status_list = db_session.get_tag_statuses()
    context.user_data["change_status_list"] = status_list
    print(status_list)

    reply_keyboard = [[text["skip"]], [text["cancel"]]]
    try:
        status_idx = context.user_data["change_status_idx"]
    except KeyError:
        status_idx = 0
    print(status_idx)
    try:
        status = status_list[status_idx][0]
    except IndexError:
        context.user_data.pop("change_status_idx")
        status = status_list[status_idx][0]

    print(status)
    context.user_data["change_status_idx"] = status_idx + 1
    tag_list = db_session.get_tags_by_status(status)
    for tag in tag_list:
        tag_name = tag.name
        reply_keyboard.append([tag_name])

    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, selective=True)

    if status == "None":
        status = "сферы"
    context.bot.send_message(
        chat_id=chat_id,
        text=f"Выберите {status}, которые лучше всего вам подходят:",
        reply_markup=markup,
    )

    return States.CHANGE_ADD_USER_TAG


def change_add_user_tag(update: Update, context: CallbackContext):
    """ pass """

    chat_id = update.message.chat.id
    mssg = update.message.text

    status_list = context.user_data["change_status_list"]
    status_idx = context.user_data["change_status_idx"]

    try:
        tag_id = db_session.get_tag_by_name(mssg).id
    except AttributeError:
        if status_idx != (len(status_list) - 1):
            return change_user_tags(update, context)
        else:
            tag_id = None

    if tag_id != None:
        try:
            user_tag_list = context.user_data["user_tag_list"]
            user_tag_list.append(tag_id)
        except KeyError:
            user_tag_list = []
            user_tag_list.append(tag_id)
            context.user_data["user_tag_list"] = user_tag_list
    else:
        try:
            user_tag_list = context.user_data["user_tag_list"]
        except KeyError:
            user_tag_list = []
            context.user_data["user_tag_list"] = user_tag_list
    print(user_tag_list)

    if status_idx == (len(status_list) - 1):
        context.user_data.pop("change_status_list")
        context.user_data.pop("user_tag_list")
        context.user_data.pop("change_status_idx")
        for user_tag in user_tag_list:
            db_session.add_user_tag(chat_id, user_tag)
        return profile(update, context)

    return change_user_tags(update, context)
