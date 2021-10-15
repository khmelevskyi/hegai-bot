""" busines logic database access """
from typing import Dict
from typing import List
from typing import Tuple

from . import _admin
from . import _registration
from ..hegai_db import Action
from ..hegai_db import User
from ..hegai_db import UserAction
from ..hegai_db import Region
from ._utils import local_session


class DBSession(_admin.Mixin, _registration.Mixin):
    """ db function with renewadle session for each func """

    def __init__(self):
        self.action_types = self.get_action_types()
        self.admins = self.get_admins()

    # @local_session
    # def get_engine(self, session, university_id: int) -> dict:
    #     """ create engine for university """
    #     engine_name, engine_parameters = (
    #         session.query(University.engine_name, University.engine_parameters)
    #         .filter(University.id == university_id)
    #         .first()
    #     )
    #     engine = {
    #         "engine_name": engine_name,
    #         "engine_parameters": engine_parameters,
    #     }
    #     return engine

    @local_session
    def get_user_data(self, session, chat_id: int) -> User:
        """ returns user by chat_id """
        user = (
            session.query(User)
            .filter(User.chat_id==chat_id).first()
        )
        return user

    @local_session
    def get_user_data_by_username(self, session, username: str) -> User:
        """ returns user by username """
        user = (
            session.query(User)
            .filter(User.username==username).first()
        )
        return user

    @local_session
    def get_all_regions(self, session) -> List[Region]:
        """ gets all regions """
        regions = session.query(Region).all()
        return regions

    @local_session
    def get_region(self, session, region_id) -> Region:
        """ gets a region object by id """
        region = session.query(Region).get(region_id)
        return region

    @local_session
    def create_region(self, session, new_region) -> None:
        """ creates a new region """
        region = Region(name=new_region)
        session.add(region)
        session.commit()

    @local_session
    def save_new_name(self, session, chat_id, new_name) -> None:
        """ saves user's new name to db """
        user = session.query(User).filter(User.chat_id==chat_id).first()
        user.full_name = new_name
        session.commit()
    
    @local_session
    def save_new_region(self, session, chat_id, new_region) -> None:
        """ saves user's new name to db """
        user = session.query(User).filter(User.chat_id==chat_id).first()
        user.region = new_region
        session.commit()
    
    @local_session
    def save_new_status(self, session, chat_id) -> None:
        """ saves user's new name to db """
        user = session.query(User).filter(User.chat_id==chat_id).first()
        if user.conversation_open == True:
            user.conversation_open = False
        else:
            user.conversation_open = True
        session.commit()

    @local_session
    def ban_user(self, session, chat_id: int) -> None:
        """ user banned the bot """

        user = session.query(User).filter(User.chat_id==chat_id).first()
        if user and user.is_banned is False:
            user.is_banned = True
            session.commit()

    @local_session
    def unban_user(self, session, chat_id: int) -> None:
        """ user started conversation after ban """

        user = session.query(User).filter(User.chat_id==chat_id).first()
        if user.is_banned is True:
            user.is_banned = False
            session.commit()

    @local_session
    def ban_multiple_users(self, session, chat_ids: List[int]) -> None:
        """ set User.is_banned to true and log banned as Action"""

        if chat_ids:
            ban_id = session.query(Action.id).filter(Action.name == "ban").first()

            users = session.query(User).filter(User.chat_id.in_(chat_ids)).all()
            for user in users:
                if user.is_banned is False:
                    user.is_banned = True

                    # log banned
                    new_action = UserAction(chat_id=user.chat_id, action=ban_id)
                    session.add(new_action)
        session.commit()

    @local_session
    def count_users(self, session) -> int:
        """ number of users in our db """

        users_quantity = session.query(User).count()
        return users_quantity

    @local_session
    def get_users_list(self, session):
        """ list all users in database """

        users = session.query(User.chat_id).all()
        return users

    @local_session
    def log_action(self, session, chat_id: int, action: str):
        """ log which action has user performed """

        action_id = self.action_types[action]
        new_action = UserAction(chat_id=chat_id, action=action_id)
        session.add(new_action)
        session.commit()

    @local_session
    def get_action_types(self, session) -> Dict[str, int]:
        """ cache actions for easier create """

        # reverse name and id
        actions = {
            value: key for key, value in session.query(Action.id, Action.name).all()
        }

        return actions


db_session: DBSession = DBSession()
