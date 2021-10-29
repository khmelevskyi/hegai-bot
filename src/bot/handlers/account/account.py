""" basic info abount user and registrarion process for student and teacher """
from telegram import ParseMode
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import Update
from telegram.ext import CallbackContext
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from loguru import logger

from ...data import start_keyboard
from ...data import text
from ...db_functions import db_session
from ...states import States
from .utils import users
from ..tags_chooser import TagsChooser

tags_chooser = TagsChooser()

# from ...db_functions import Action


def profile(update: Update, context: CallbackContext):
    """ basic account info """
    logger.info("showing profile")
    try:
        chat_id = update.message.chat.id
    except AttributeError:
        chat_id = update.callback_query.message.chat.id

    if chat_id in users:  # if user returned from registration form
        users.pop(chat_id, None)

    user = db_session.get_user_data(chat_id)

    # db_session.log_action(chat_id=chat_id, action=Action.profile)

    if user.notion_id is None:
        context.bot.send_message(chat_id=chat_id, text=text["not_registered"])
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
    logger.info("changing name")

    chat_id = update.message.chat.id

    reply_keyboard = [
        [text["cancel"]],
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, selective=True)

    context.bot.send_message(
        chat_id=chat_id, text="Введите новое имя:", reply_markup=markup
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
    logger.info("changing region")

    chat_id = update.message.chat.id

    regions = db_session.get_all_regions()

    reply_keyboard = []
    for region in regions:
        reply_keyboard.append([region.name])
    reply_keyboard.append([text["cancel"]])

    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, selective=True)

    context.bot.send_message(
        chat_id=chat_id, text="Выберите регион:", reply_markup=markup
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
    logger.info("changing status")

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
        text=f"Поменять статус на: <b>{status_text}</b>?",
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
    logger.info("changing user tags")

    chat_id = update.message.chat.id
    tags_chooser.flush()

    user_tags = db_session.get_user_tags(chat_id)
    if len(user_tags) > 0:
        user_tags = db_session.get_user_tags(chat_id)
        for user_tag in user_tags:
            user_tag_id = user_tag.id
            db_session.remove_user_tag(user_tag_id)

    status_list = [ii[0] for ii in db_session.get_tag_statuses()]
    print(status_list)
    tags_chooser.statuses = status_list

    show_page(update, context)

    return States.CHANGE_CHOOSING_TAGS


def show_page(update: Update, context: CallbackContext):
    """ showing page of user tags """
    try:
        chat_id = update.message.chat.id
    except AttributeError:
        chat_id = update.callback_query.message.chat.id

    tags_chooser.status_tags = tags_chooser.curr_status

    tags = tags_chooser.page_tags
    print(tags)

    inline_keyboards = []
    for ii in range(0, len(tags), 2):
        tag = tags[ii]
        if len(tags) % 2 != 0 and ii == len(tags) - 1:
            inline_keyboards.append(
                [
                    InlineKeyboardButton(
                        text=tags[ii].name, callback_data=f"tag-{tags[ii].name}"
                    )
                ]
            )
        else:
            tag_n = tags[ii + 1]
            inline_keyboards.append(
                [
                    InlineKeyboardButton(
                        text=tag.name, callback_data=f"tag-{tag.name}"
                    ),
                    InlineKeyboardButton(
                        text=tag_n.name, callback_data=f"tag-{tag_n.name}"
                    ),
                ]
            )

    inline_keyboards.append(
        [
            InlineKeyboardButton(text="⬅", callback_data="back"),
            InlineKeyboardButton(text="➡", callback_data="next"),
        ]
    )
    inline_keyboards.append(
        [InlineKeyboardButton(text=text["cancel"], callback_data="cancel")]
    )

    if tags_chooser.curr_status == tags_chooser.statuses[-1]:
        inline_keyboards.append(
            [InlineKeyboardButton(text=text["finish"], callback_data="finish_t")]
        )
    else:
        inline_keyboards.append(
            [
                InlineKeyboardButton(
                    text=text["next_category"], callback_data="category_n"
                )
            ]
        )

    markup = InlineKeyboardMarkup(
        inline_keyboards,
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    try:
        if tags_chooser.curr_status == "None":
            update.callback_query.edit_message_text("Выберите Сферы")
        else:
            update.callback_query.edit_message_text(
                f"Выберите {tags_chooser.curr_status}"
            )
        update.callback_query.edit_message_reply_markup(markup)
    except AttributeError:
        context.bot.send_message(
            chat_id=chat_id,
            text=f"Выберите {tags_chooser.curr_status}",
            reply_markup=markup,
        )

    return States.CHANGE_CHOOSING_TAGS


def change_add_user_tag(update: Update, context: CallbackContext):
    """ adding user tag to db """
    logger.info("adding user tag")

    chat_id = update.callback_query.message.chat.id
    update.callback_query.answer("Тэг успешно добавлен!")
    data = update.callback_query.data
    print(data)

    tag_name = data.replace("tag-", "")

    tag_id = db_session.get_tag_by_name(tag_name).id

    db_session.add_user_tag(chat_id, tag_id)

    # show_page(update, context)


def change_next_back_page_tags(update: Update, context: CallbackContext):
    """ changing page of user tags to next/back """
    update.callback_query.answer()
    data = update.callback_query.data
    print(data)

    tags_chooser.page = data

    show_page(update, context)


def change_next_category_tags(update: Update, context: CallbackContext):
    """ changing status of user tags to next """
    update.callback_query.answer()
    data = update.callback_query.data
    print(data)

    tags_chooser.page = "new"
    tags_chooser.curr_status = data

    show_page(update, context)
