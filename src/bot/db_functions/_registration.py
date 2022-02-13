""" db for regsistation workflow """
from telegram import Chat

from ..hegai_db import User
from ._utils import local_session


class Mixin:
    """ registration """

    @local_session
    def add_user(self, session, chat: Chat) -> User:
        """
        Create user record if not exist, otherwise update username
        """
        chat_id = chat.id
        try:
            username = chat.username.lower()
        except AttributeError:
            username = chat.username
        first_name = chat.first_name

        user = session.query(User).filter(User.username == username).first()
        if user:
            if user.chat_id != chat_id:
                user.chat_id = chat_id
                session.commit()
            if user.is_banned is True:
                user.is_banned = False
                session.commit()
            return user

        if username == None:
            new_user = User(
                chat_id=chat_id,
                # notion_id=None,
                # conversation_open=None,
                is_banned=False,
                # region=None,
                # username=username,
                full_name=first_name,
            )
        else:
            new_user = User(
                chat_id=chat_id,
                # notion_id=None,
                # conversation_open=None,
                is_banned=False,
                # region=None,
                username=username,
                full_name=first_name,
            )
        session.add(new_user)
        session.commit()
        return new_user

    @local_session
    def user_is_registered(self, session, chat_id: int) -> bool:
        """
        Create user record if not exist, otherwise update username
        """
        user = session.query(User).filter(User.chat_id == chat_id).first()
        try:
            if user.notion_id:
                return True
            return False
        except AttributeError:
            return False

    @local_session
    def add_user_data(
        self,
        session,
        chat: Chat,
        notion_id: str,
        username: str,
        conversation_open,
        conv_requests_week_max,
    ):
        """ save user settings for api request """

        chat_id = chat.id

        user: User = session.query(User).filter(User.username == username).first()
        if not user:
            user = self.add_user(chat)
        user.notion_id = notion_id
        user.chat_id = chat_id
        user.conversation_open = conversation_open
        user.conv_requests_week_max = conv_requests_week_max
        session.commit()
