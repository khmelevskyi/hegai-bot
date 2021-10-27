""" class to contain push data """
from typing import Callable
from typing import Tuple

from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import ParseMode
from telegram.ext import CallbackContext
from telegram.message import Message


class PushMessage:
    """ container for data to be pushed """

    def __init__(self):
        self.message: Message = None
        self._button: InlineKeyboardButton = None

    @property
    def button(self) -> InlineKeyboardButton:
        """button"""
        return self._button

    @button.setter
    def button(self, data: Tuple[str, str]):
        """ create button """
        self._button = InlineKeyboardButton(data[0], url=data[1])

    @button.deleter
    def button(self):
        """ flush button """
        self._button = None

    @property
    def kwargs(self) -> dict:
        """ collect kward for broadcast_func """

        msg = self.message
        if msg.photo:
            push_kwargs = {"photo": msg.photo[-1], "caption": msg.caption_html}
        else:
            push_kwargs = {"text": msg.text_html, "disable_web_page_preview": True}

        if self.button:
            push_kwargs["reply_markup"] = InlineKeyboardMarkup([[self.button]])
        push_kwargs["parse_mode"] = ParseMode.HTML
        return push_kwargs

    def get_broadcast_func(self, context: CallbackContext) -> Callable:
        """ get appropriate functuin type """
        if self.message.photo:
            return context.bot.send_photo
        return context.bot.send_message

    def flush(self):
        """ clean function """
        self.message: Message = None
        del self.button
