from loguru import logger
from telegram import error as e


def check_user(f):
    def wrapper(*args):
        try:
            # args[0] is update
            if args[0].effective_user.is_bot:
                logger.warning(
                    "Attempt to login from bot with id: {} and name: {}".format(
                        args[0].effective_user.bot.id, args[0].effective_user.bot.name
                    )
                )
                args[0].message.reply_text("Bots are not allowed!")
                return
            else:
                f(*args)

        except (e.BadRequest, e.Unauthorized) as err:
            logger.error("Error: {}\nUser: {}".format(err, args[0].effective_user.id))

    return wrapper
