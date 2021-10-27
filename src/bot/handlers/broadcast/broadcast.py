""" send push notifications to all users """
import time
from typing import Callable
from typing import List
from typing import Optional
from typing import Tuple

from telegram import Update
from telegram.error import BadRequest
from telegram.error import ChatMigrated
from telegram.error import Unauthorized
from telegram.ext import CallbackContext
from telegram.parsemode import ParseMode

from .push_status import PushStatus
from ...utils import restricted
from ...db_functions import db_session
from ...hegai_db import Permission


push_status = PushStatus()


@restricted(Permission.PUSH)
def broadcast_status(update: Update, context: CallbackContext):
    """ form msg about push status """

    push_status_render = push_status.render()
    update.message.reply_text(push_status_render)


def run_broadcast(
    broadcast_func: Callable,  # send func
    users: List[Tuple[int, bool]],  # chat_ids, is_banned
    push_kwargs: dict,  # config for push func
    msgs: dict,  # custom msg for each user
    update: Optional[Update] = None,  # send msg about results
):
    """ iterate trough users and send msgs """

    failed_users = {}
    fixed_users = []
    new_fails = 0

    def record_failed(error, chat_id: int, is_banned: bool):
        nonlocal new_fails
        nonlocal failed_users

        error_dict = {
            "error_class": type(error).__name__,
            "error_message": error.message if hasattr(error, "message") else str(error),
        }
        if not is_banned:  # new bans
            new_fails += 1
        push_status.error_send += 1
        failed_users[chat_id] = (is_banned, error_dict)

    def record_fixed(chat_id: int, is_banned: bool):
        nonlocal fixed_users

        push_status.successful_send += 1
        if is_banned:  # user was banned, but now is available
            fixed_users.append(chat_id)

    # keep track of push data
    push_status.push_is_active = True
    push_status.total_receivers = len(users)

    for chat_id, is_banned in users:
        print(chat_id)
        msg_start_time = time.time()

        if msg_text := msgs.get(chat_id):
            push_kwargs["text"] = msg_text

        try:
            broadcast_func(chat_id=chat_id, **push_kwargs)
            record_fixed(chat_id, is_banned)
        except ChatMigrated as error:
            new_chat_id = error.new_chat_id
            # rozklad_api.user(chat_id).migrate(new_chat_id)
            users.append((new_chat_id, False))
        except (Unauthorized, BadRequest) as error:  # bot was banned
            record_failed(error, chat_id, is_banned)
        except Exception as error:
            record_failed(error, chat_id, is_banned)

        broadcast_await(msg_start_time)

    # update db
    db_session.ban_users(failed_users)
    db_session.unban_users(fixed_users)

    if update:
        # ignore stats if it's invoked by timer
        db_changes = {
            # count new bans
            "failed_users": new_fails,
            "fixed_users": len(fixed_users),
        }
        update.message.reply_text(
            push_status.render(db_changes), parse_mode=ParseMode.HTML
        )

    push_status.flush()  # clean data about the push


def broadcast_await(msg_start_time: float):
    """ await beetwean msgs to keep spam limit safe """

    single_broadcast_time = time.time() - msg_start_time
    # spam_limit_time = 0.05  # 1/20 of a second due to spam limit of 30 msgs per second
    # await up to spam_limit_time in case post worked to fast
    if single_broadcast_time < 0.05:
        await_time = 0.05 - single_broadcast_time
        time.sleep(await_time)
