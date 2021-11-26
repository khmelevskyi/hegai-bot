""" find a conversation module """
import re
from os import getenv

from telegram import ParseMode
from telegram import ReplyKeyboardMarkup
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import ConversationHandler
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from loguru import logger

from ...data import text
from ...db_functions import db_session
from ...states import States
from ..handlers import start
from ..tags_chooser import TagsChooser
from ..account import get_profile

tags_chooser = TagsChooser()


def default_or_choose(update: Update, context: CallbackContext):
    """ asks user whether to use his profile tags or choose new ones """
    chat_id = update.message.chat.id

    conv_request = db_session.get_conv_request_active_by_user_id(chat_id)
    if conv_request:

        reply_keyboard = [
            [text["ok"]],
            [text["cancel_request"]],
        ]
        markup = ReplyKeyboardMarkup(
            reply_keyboard, resize_keyboard=True, selective=True
        )

        context.bot.send_message(
            chat_id=chat_id,
            text="У Вас уже есть активный запрос на разговор, мы Вас оповестим, когда найдем кого-то!",
            reply_markup=markup,
        )
        return States.EXISTING_REQUEST

    reply_keyboard = [
        [text["use_profile_tags"]],
        [text["choose_tags_yourself"]],
        [text["back"]],
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, selective=True)

    context.bot.send_message(
        chat_id=chat_id,
        text="Использовать теги из Вашего профиля или хотите выбрать теги для поиска вручную?",
        reply_markup=markup,
    )

    return States.DEFAULT_TAGS_OR_NEW


def ask_conv_filters(update: Update, context: CallbackContext):
    """ asks user for filters for finding a conversation """
    logger.info("asking for user tags")

    chat_id = update.message.chat.id
    answer = update.message.text
    tags_chooser.flush()

    user = db_session.get_user_data(chat_id)

    user_tags = db_session.get_user_tags(chat_id)
    for user_tag in user_tags:
        db_session.remove_user_tag(user_tag.id)

    if answer == text["use_profile_tags"]:
        profile_data = get_profile(update, context, user.notion_id)
        if profile_data == None:
            return start(update, context)
        tags = profile_data["Function"] + profile_data["Industry"]
        print(tags)
        for tag in tags:
            try:
                tag_id = db_session.get_tag_by_name(tag).id
            except AttributeError:
                continue
            db_session.add_user_tag(chat_id, tag_id)
        return create_conv_request(update, context)

    status_list = ["Компетенции", "Отрасли"]
    print(status_list)
    tags_chooser.statuses = status_list

    show_page(update, context)

    return States.CHOOSING_TAGS


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

    if len(tags) < 8 and tags_chooser.page == 0:
        pass
    elif len(tags) < 8:
        inline_keyboards.append(
            [
                InlineKeyboardButton(text="⬅", callback_data="back"),
            ]
        )
    elif tags_chooser.page == 0:
        inline_keyboards.append(
            [
                InlineKeyboardButton(text="➡", callback_data="next"),
            ]
        )
    else:
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
        update.callback_query.edit_message_text(f"Выберите {tags_chooser.curr_status}")
        update.callback_query.edit_message_reply_markup(markup)
    except AttributeError:
        context.bot.send_message(
            chat_id=chat_id,
            text=f"Выберите {tags_chooser.curr_status}",
            reply_markup=markup,
        )

    return States.CHANGE_CHOOSING_TAGS


def add_user_tag(update: Update, context: CallbackContext):
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


def next_back_page_tags(update: Update, context: CallbackContext):
    """ changing page of user tags to next/back """
    update.callback_query.answer()
    data = update.callback_query.data
    print(data)

    tags_chooser.page = data

    show_page(update, context)


def next_category_tags(update: Update, context: CallbackContext):
    """ changing status of user tags to next """
    update.callback_query.answer()
    data = update.callback_query.data
    print(data)

    tags_chooser.page = "new"
    tags_chooser.curr_status = data

    show_page(update, context)


def create_conv_request(update: Update, context: CallbackContext):
    """ creating a new conv request and adding to db """
    logger.info("creating conv request")

    try:
        chat_id = update.message.chat.id
    except AttributeError:
        chat_id = update.callback_query.message.chat.id

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
    logger.info("cancelling conv request")

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
    logger.info("finding conversation")

    user_tags = conv_request.tags
    user_tags_sorted = sorted(user_tags)
    print(user_tags_sorted)
    potential_users = db_session.get_open_users()
    contacts = db_session.get_contacts(conv_request.user_id)
    contacts = [ii[0] for ii in contacts]
    for user in potential_users:

        if user.id != conv_request.user_id and user.id not in contacts:
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
    logger.info("user for conversation found")

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
        text=f"Мы нашли вам партнера! Встречайте @{user_two.username}\n\n"
        f"Ваши общие интересы: {common_tags_final}\n\n"
        "Напишите собеседнику в Телеграм прямо сейчас и договоритесь о встрече онлайн или вживую",
    )
    context.bot.send_message(
        chat_id=user_two.chat_id,
        text=f"Мы предпологаем вы можете быть полезны друг другу! Встречайте @{user_one.username}\n\n"
        f"Ваши общие интересы: {common_tags_final}\n\n"
        "Напишите собеседнику в Телеграм прямо сейчас и договоритесь о встрече онлайн или вживую",
    )


def user_not_found(conv_request, context):
    """user not found function """
    logger.info("user for conversation NOT found, sending info to support")

    user_one_id = conv_request.user_id
    user_one = db_session.get_user_data_by_id(user_one_id)
    context.bot.send_message(
        chat_id=user_one.chat_id,
        text="К сожалению, бот не нашел Вам партнера по вашим интересам(\nНо наши администраторы найдут!\nС Вами свяжутся в ближайшем времени",
    )

    user_tags = db_session.get_user_tags(user_one.chat_id)
    text_tags = "\n"
    status_list = ["Компетенции", "Отрасли"]
    for status in status_list:
        status_name = status
        has_tags = False
        text_status = f"Категория: {status_name}\n"
        for user_tag in user_tags:
            tag = db_session.get_tag(user_tag.tag_id)
            if status_name == tag.status:
                text_status += f"\t\t • {tag.name}\n"
                has_tags = True
        if has_tags is True:
            text_tags += text_status

    context.bot.send_message(
        chat_id=getenv("GROUP_ID"),
        text=(
            f"Не удалось найти партнера для данного пользователя: @{user_one.username}\n"
            + f"Имя: {user_one.full_name}\nРегион: {user_one.region}\n"
            + f"Notion id: {user_one.notion_id}\n"
            + f"<b>Теги: {text_tags}</b>"
        ),
        parse_mode=ParseMode.HTML,
    )


def support_reply(update: Update, context: CallbackContext):
    """ parses support reply for conv request and sends initial user found partner """
    logger.info("getting support reply")

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

    try:
        username = re.search(r"@(\w*)", mssg_replied).group(0).replace("@", "")
    except AttributeError:
        context.bot.send_message(
            chat_id=update.message.chat.id,
            text="Извините, но Вы ответили реплаем не на то сообщение!'\nОтправьте ссылку на подходящего человека в виде 'https://www.notion.so/phegai/ссылка_на_человека' реплаем на соотвествующее сообщение",
        )
        return States.SUPPORT_REPLY

    user = db_session.get_user_data_by_username(username)

    user_found = db_session.get_user_data_by_notion_id(user_found_notion_id)

    conv_request = db_session.get_conv_request_active_by_user_id(user.chat_id)
    try:
        db_session.update_conv_request(conv_request, user_found)
    except ValueError:
        pass

    db_session.add_contacts(user.id, user_found.id)
    db_session.add_contacts(user_found.id, user.id)

    if user_found.chat_id == None:
        context.bot.send_message(
            chat_id=update.message.chat.id,
            text="Извините, но данный пользователь еще ни разу не пользовался ботом 'Хегай Нетворкинг'\nОтправьте ссылку на подходящего человека в виде 'https://www.notion.so/phegai/ссылка_на_человека' реплаем на соотвествующее сообщение",
        )
        return States.SUPPORT_REPLY

    update.message.reply_text(
        text="Спасибо, сообщение о собеседнике доставлено пользователю",
        # reply_to_message_id=
    )

    context.bot.send_message(
        chat_id=user.chat_id,
        text=f"Мы нашли Вам партнера: @{user_found.username} 🎉"
        "\n\nНапишите собеседнику в Телеграм прямо сейчас и договоритесь о встрече онлайн или вживую",
    )
    context.bot.send_message(
        chat_id=user_found.chat_id,
        text=f"Мы предпологаем вы можете быть полезны друг другу! Встречайте @{user.username} 🎉"
        "\n\nНапишите собеседнику в Телеграм прямо сейчас и договоритесь о встрече онлайн или вживую",
    )

    return ConversationHandler.END
