""" find a conversation module """
import re
from os import getenv

from telegram import ReplyKeyboardMarkup
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import ConversationHandler

from ...data import text
from ...db_functions import db_session
from ...states import States
from ..handlers import start


def ask_conv_filters(update: Update, context: CallbackContext):
    """ asks user for filters for finding a conversation """

    chat_id = update.message.chat.id

    user_tags = db_session.get_user_tags(chat_id)
    if len(user_tags) > 0:
        return create_conv_request(update, context)

    status_list = db_session.get_tag_statuses()
    context.user_data["status_list"] = status_list
    print(status_list)

    reply_keyboard = [[text["skip"]], [text["cancel"]]]
    try:
        status_idx = context.user_data["status_idx"]
    except KeyError:
        status_idx = 0
    print(status_idx)
    try:
        status = status_list[status_idx][0]
    except IndexError:
        context.user_data.pop("status_idx")
        status = status_list[status_idx][0]

    print(status)
    context.user_data["status_idx"] = status_idx + 1
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

    return States.ADD_USER_TAG


def add_user_tag(update: Update, context: CallbackContext):
    """ pass """

    chat_id = update.message.chat.id
    mssg = update.message.text

    status_list = context.user_data["status_list"]
    status_idx = context.user_data["status_idx"]

    try:
        tag_id = db_session.get_tag_by_name(mssg).id
    except AttributeError:
        return ask_conv_filters(update, context)

    try:
        user_tag_list = context.user_data["user_tag_list"]
        user_tag_list.append(tag_id)
    except KeyError:
        user_tag_list = []
        user_tag_list.append(tag_id)
        context.user_data["user_tag_list"] = user_tag_list
    print(user_tag_list)

    if status_idx == (len(status_list) - 1):
        context.user_data.pop("status_list")
        context.user_data.pop("user_tag_list")
        context.user_data.pop("status_idx")
        for user_tag in user_tag_list:
            db_session.add_user_tag(chat_id, user_tag)
        return create_conv_request(update, context)

    return ask_conv_filters(update, context)


def create_conv_request(update: Update, context: CallbackContext):
    """ pass """

    chat_id = update.message.chat.id

    conv_request = db_session.get_conv_request_active_by_user_id(chat_id)
    if conv_request:

        reply_keyboard = [[text["ok"]], [text["cancel_request"]]]
        markup = ReplyKeyboardMarkup(
            reply_keyboard, resize_keyboard=True, selective=True
        )

        context.bot.send_message(
            chat_id=chat_id,
            text="У Вас уже есть активный запрос на разговор, мы Вас оповестим, когда найдем кого-то!",
            reply_markup=markup,
        )
        return States.EXISTING_REQUEST

    context.bot.send_message(
        chat_id=chat_id,
        text="Отлично! Ищем для Вас собеседника...",
    )

    conv_request = db_session.create_conv_request(chat_id)
    conv_request = db_session.get_conv_request_active_by_user_id(chat_id)

    result = find_conversation(conv_request, context)

    if result is False:
        user_not_found(conv_request, context)

    return start(update, context)


def cancel_request(update: Update, context: CallbackContext):
    """ cancel conv request and deletes from db """
    chat_id = update.message.chat.id

    conv_request = db_session.get_conv_request_active_by_user_id(chat_id)
    db_session.remove_active_conv_request(conv_request.id)

    context.bot.send_message(
        chat_id=chat_id,
        text="Мы отменили прошлый запрос на общение! Теперь Вы можете еще раз попробывать найти собеседника",
    )
    return start(update, context)


def find_conversation(conv_request, context):
    """ checks through all open users wether they have the same tags """
    user_tags = conv_request.tags
    user_tags_sorted = sorted(user_tags)
    print(user_tags_sorted)
    potential_users = db_session.get_open_users()
    for user in potential_users:

        if user.id != conv_request.user_id:
            user_two_tags = db_session.get_user_tags_by_user_id(user.id)
            user_two_tags_names = []
            for user_two_tag in user_two_tags:
                tag_name = db_session.get_tag(user_two_tag.tag_id).name
                user_two_tags_names.append(tag_name)
            user_two_tags_sorted = sorted(user_two_tags_names)

            common_tags = [tt for tt in user_tags_sorted if tt in user_two_tags_sorted]

            if len(common_tags) >= 2:
                user_found(conv_request, user, common_tags, context)
                return True

    return False


def user_found(conv_request, user_found, common_tags, context):
    """ user found function """
    db_session.update_conv_request(conv_request, user_found, common_tags)

    common_tags_str = str(common_tags)
    common_tags_final = (
        common_tags_str.replace("'", "").replace("[", "").replace("]", "")
    )

    user_one_id = conv_request.user_id
    user_one = db_session.get_user_data_by_id(user_one_id)
    user_two = db_session.get_user_data_by_id(user_found.id)
    db_session.add_contacts(user_one.id, user_two.id)
    db_session.add_contacts(user_two.id, user_one.id)
    context.bot.send_message(
        chat_id=user_one.chat_id,
        text=f"Мы нашли вам партнера! Встречайте @{user_two.username}\n\nВаши общие интересы: {common_tags_final}",
    )


def user_not_found(conv_request, context):
    """user not found function """
    user_one_id = conv_request.user_id
    user_one = db_session.get_user_data_by_id(user_one_id)
    context.bot.send_message(
        chat_id=user_one.chat_id,
        text="К сожалению, бот не нашел Вам партнера по вашим интересам(\nНо наши администраторы найдут!\nС Вами свяжутся в ближайшем времени",
    )

    user_tags = db_session.get_user_tags(user_one.chat_id)
    user_tags_names = []
    for user_tag in user_tags:
        tag_name = db_session.get_tag(user_tag.tag_id).name
        user_tags_names.append(tag_name)
    user_tags_names = (
        str(user_tags_names).replace("'", "").replace("[", "").replace("]", "")
    )

    context.bot.send_message(
        chat_id=getenv("GROUP_ID"),
        text=(
            f"Не удалось найти партнера для данного пользователя: @{user_one.username}\n"
            + f"Имя: {user_one.full_name}\nРегион: {user_one.region}\n"
            + f"Теги: {user_tags_names}"
            + f"Notion id: {user_one.notion_id}"
        ),
    )


def support_reply(update, context):
    """ parses support reply for conv request and sends initial user found partner """
    mssg = update.message.text
    if "notion.so" not in mssg:
        context.bot.send_message(
            chat_id=update.message.chat.id,
            text="Извините, но это неправильный формат\nОтправьте ссылку на подходящего человека в виде 'https://www.notion.so/phegai/ссылка_на_человека' реплаем на соотвествующее сообщение",
        )
        return States.SUPPORT_REPLY
    else:
        user_found_notion_id = mssg.replace("https://www.notion.so/phegai/", "")
        user_found_notion_id = (
            user_found_notion_id[:8]
            + "-"
            + user_found_notion_id[8:12]
            + "-"
            + user_found_notion_id[12:16]
            + "-"
            + user_found_notion_id[16:20]
            + "-"
            + user_found_notion_id[20:32]
        )

    mssg_replied = update.message.reply_to_message.text

    username = re.search(r"@(\w*)", mssg_replied).group(0).replace("@", "")
    user = db_session.get_user_data_by_username(username)

    user_found = db_session.get_user_data_by_notion_id(user_found_notion_id)

    conv_request = db_session.get_conv_request_active_by_user_id(user.chat_id)
    db_session.update_conv_request(conv_request, user_found)

    db_session.add_contacts(user.id, user_found.id)
    db_session.add_contacts(user_found.id, user.id)

    context.bot.send_message(
        chat_id=user.chat_id,
        text=f"Мы нашли Вам партнера: @{user_found.username}",
    )

    return ConversationHandler.END
