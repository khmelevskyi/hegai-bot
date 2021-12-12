""" busines logic database access """
from datetime import timedelta
from typing import Dict
from typing import List
from typing import Tuple

from . import _admin
from . import _registration
from ..hegai_db import Action
from ..hegai_db import Contacts
from ..hegai_db import ConversationRequest
from ..hegai_db import Feedback
from ..hegai_db import local_time
from ..hegai_db import Region
from ..hegai_db import Tag
from ..hegai_db import User
from ..hegai_db import UserAction
from ..hegai_db import UserTag
from ._utils import local_session


class DBSession(_admin.Mixin, _registration.Mixin):
    """ db function with renewadle session for each func """

    def __init__(self):
        self.action_types = self.get_action_types()
        self.admins = self.get_admins()

    @local_session
    def get_all_users(self, session) -> List:
        """ returns all users """
        users = session.query(User).all()
        return users

    @local_session
    def get_all_users_for_broadcast(self, session) -> List[Tuple[int, bool]]:
        """ returns all users ids and is_banned """
        users = session.query(User.chat_id, User.is_banned).all()
        return users

    @local_session
    def get_all_users_for_broadcast_by_region(
        self, session, region
    ) -> List[Tuple[int, bool]]:
        """ returns all users ids and is_banned by the specific region """
        region_id = self.get_region_by_name(region).id
        users = (
            session.query(User.chat_id, User.is_banned)
            .filter(User.region == region_id)
            .all()
        )
        return users

    @local_session
    def get_all_users_by_region(self, session, region) -> List:
        """ returns all users by the specific region """
        region_id = self.get_region_by_name(region).id
        users = session.query(User).filter(User.region == region_id).all()
        return users

    @local_session
    def get_all_usernames(self, session) -> List:
        """ returns all usernames from db """
        usernames_list = session.query(User.username).all()
        usernames = [username[0] for username in usernames_list]
        return usernames

    @local_session
    def get_open_users(self, session) -> List:
        """ returns all users who are open for conversation """
        users = session.query(User).filter(User.conversation_open == True).all()
        return users

    @local_session
    def get_user_data(self, session, chat_id: int) -> User:
        """ returns user by chat_id """
        user = session.query(User).filter(User.chat_id == chat_id).first()
        return user

    @local_session
    def get_user_data_by_id(self, session, id: int) -> User:
        """ returns user by id """
        user = session.query(User).get(id)
        return user

    @local_session
    def get_user_data_by_username(self, session, username: str) -> User:
        """ returns user by username """
        user = session.query(User).filter(User.username == username).first()
        return user

    @local_session
    def get_user_data_by_notion_id(self, session, notion_id: str) -> User:
        """ returns user by notion_id """
        user = session.query(User).filter(User.notion_id == notion_id).first()
        return user

    @local_session
    def get_contacts(self, session, id: int) -> List:
        """ returns user's contact's ids """
        contacts = (
            session.query(Contacts.user_two).filter(Contacts.user_one == id).all()
        )
        return contacts

    @local_session
    def add_contacts(self, session, user_one_id: int, user_two_id: int) -> None:
        """ adds a contacts row to db """
        contacts = (
            session.query(Contacts)
            .filter(Contacts.user_one == user_one_id, Contacts.user_two == user_two_id)
            .first()
        )
        if contacts:
            pass
        else:
            new_contacts = Contacts(user_one=user_one_id, user_two=user_two_id)
            session.add(new_contacts)
            session.commit()

    @local_session
    def get_tag(self, session, tag_id) -> Tag:
        """ returns tag by its id """
        tag = session.query(Tag).get(tag_id)
        return tag

    @local_session
    def get_tag_by_notion_id(self, session, notion_id: str) -> Tag:
        """ returns tag by notion_id """
        tag = session.query(Tag).filter(Tag.notion_id == notion_id).first()
        return tag

    @local_session
    def get_tag_by_name(self, session, tag_name: str) -> Tag:
        """ returns a tag by name """
        tag = session.query(Tag).filter(Tag.name == tag_name).first()
        return tag

    @local_session
    def get_tag_statuses(self, session) -> List:
        """ returns all tags' statuses """
        statuses = session.query(Tag.status).all()
        statuses = list(dict.fromkeys(statuses))
        return statuses

    @local_session
    def get_tags_by_status(self, session, status: str) -> List:
        """ returns all tags by status """
        tags = session.query(Tag).filter(Tag.status == status).all()
        return tags

    @local_session
    def get_user_tags(self, session, chat_id) -> List:
        """ returns all user tags by chat_id """
        user_id = self.get_user_data(chat_id).id
        user_tags = session.query(UserTag).filter(UserTag.user_id == user_id).all()
        return user_tags

    @local_session
    def get_user_tags_by_notion_id(self, session, notion_id) -> List:
        """ returns all user tags by notion_id """
        user_id = self.get_user_data_by_notion_id(notion_id).id
        user_tags = session.query(UserTag).filter(UserTag.user_id == user_id).all()
        return user_tags

    @local_session
    def get_user_tags_by_user_id(self, session, user_id) -> List:
        """ returns all user tags by chat_id """
        user_tags = session.query(UserTag).filter(UserTag.user_id == user_id).all()
        return user_tags

    @local_session
    def add_user_tag(self, session, chat_id, tag_id) -> None:
        """ saves a new user tag to db """
        user_id = self.get_user_data(chat_id).id
        user_tag = UserTag(user_id=user_id, tag_id=tag_id)
        session.add(user_tag)
        session.commit()

    @local_session
    def add_user_tag_by_notion_id(self, session, notion_id, tag_id) -> None:
        """ pass """
        user_id = self.get_user_data_by_notion_id(notion_id).id
        user_tag = UserTag(user_id=user_id, tag_id=tag_id)
        session.add(user_tag)
        session.commit()

    @local_session
    def remove_user_tag(self, session, user_tag_id) -> None:
        """ deletes user tag """
        user_tag = session.query(UserTag).get(user_tag_id)
        session.delete(user_tag)
        session.commit()

    @local_session
    def get_conv_request_active_by_user_id(
        self, session, chat_id
    ) -> ConversationRequest:
        """ returns active conversation request by user_id """
        user_id = self.get_user_data(chat_id).id
        conv_request = (
            session.query(ConversationRequest)
            .filter(
                ConversationRequest.user_id == user_id,
                ConversationRequest.active == True,
                ConversationRequest.user_found == None,
            )
            .first()
        )
        return conv_request

    @local_session
    def create_conv_request(self, session, chat_id) -> None:
        """ creates a new conv request """
        user = self.get_user_data(chat_id)
        user_tags = self.get_user_tags(chat_id)
        user_tags_names = []
        for user_tag in user_tags:
            tag_name = self.get_tag(user_tag.tag_id).name
            user_tags_names.append(tag_name)

        conv_request = ConversationRequest(
            user_id=user.id, tags=user_tags_names, active=True, time_posted=local_time()
        )
        session.add(conv_request)
        session.commit()

    @local_session
    def update_conv_request(
        self, session, conv_request, user_found, user_tags=None
    ) -> None:
        """ updates a conv request """
        conv_request_id = conv_request.id
        conv_request = session.query(ConversationRequest).get(conv_request_id)
        if user_tags == None:
            conv_request.user_found = user_found.id
            # conv_request.active = False
            conv_request.time_processed = local_time()
        else:
            conv_request.user_found = user_found.id
            conv_request.tags = user_tags
            # conv_request.active = False
            conv_request.time_processed = local_time()
        session.commit()

    @local_session
    def remove_active_conv_request(self, session, conv_request_id) -> None:
        """ removes active conv request """
        conv_request = session.query(ConversationRequest).get(conv_request_id)
        session.delete(conv_request)
        session.commit()

    @local_session
    def make_conv_request_inactive(self, session, conv_request_id) -> None:
        """ update conv request to inactive """
        conv_request = session.query(ConversationRequest).get(conv_request_id)
        conv_request.active = False
        session.commit()

    @local_session
    def get_conv_requests_more_3_days_active(
        self, session
    ) -> List[ConversationRequest]:
        """ returns all the conversation requests that are active and time.now() - time_created() => 3 days """
        conv_requests = session.query(ConversationRequest).filter(
            ConversationRequest.active == True,
            ConversationRequest.user_found != None,
            ConversationRequest.time_posted <= local_time() - timedelta(days=3),
        )
        return conv_requests.all()

    @local_session
    def get_conv_request_more_3_days_active_by_chat_id(self, session, chat_id):
        """ returns all the conversation requests that are active and time.now() - time_created() => 3 days """
        user = self.get_user_data(chat_id)
        conv_request = session.query(ConversationRequest).filter(
            ConversationRequest.user_id == user.id,
            ConversationRequest.active == True,
            ConversationRequest.time_posted <= local_time() - timedelta(days=3),
        )
        return conv_request.first()

    @local_session
    def create_success_feedback(self, session, request_id: int, rate: int) -> None:
        """ saves successful conversation feedback to db """
        feedback = Feedback(request_id=request_id, conversation_occured=True, rate=rate)
        session.add(feedback)
        session.commit()

    @local_session
    def create_not_success_feedback(
        self, session, request_id: int, comment: str
    ) -> None:
        """ saves successful conversation feedback to db """
        feedback = Feedback(
            request_id=request_id, conversation_occured=False, comment=comment
        )
        session.add(feedback)
        session.commit()

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
    def get_region_by_name(self, session, region_name) -> Region:
        """ gets a region object by id """
        region = session.query(Region).filter(Region.name == region_name).first()
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
        user = session.query(User).filter(User.chat_id == chat_id).first()
        user.full_name = new_name
        session.commit()

    @local_session
    def save_new_region(self, session, notion_id, new_region) -> None:
        """ saves user's new name to db """
        user = session.query(User).filter(User.notion_id == notion_id).first()
        user.region = new_region
        session.commit()

    @local_session
    def save_new_status(self, session, chat_id) -> None:
        """ saves user's new status to db """
        user = session.query(User).filter(User.chat_id == chat_id).first()
        if user.conversation_open == True:
            user.conversation_open = False
        else:
            user.conversation_open = True
        session.commit()

    @local_session
    def get_total_feedback_yes(self, session):
        """ returns total amount of yes feedbacks """

        feedbacks_yes = (
            session.query(Feedback)
            .filter(Feedback.rate != None, Feedback.conversation_occured == True)
            .count()
        )

        return feedbacks_yes

    @local_session
    def get_total_feedback_no(self, session):
        """ returns total amount of yes feedbacks """

        feedbacks_no = (
            session.query(Feedback)
            .filter(Feedback.comment != None, Feedback.conversation_occured == False)
            .count()
        )

        return feedbacks_no

    @local_session
    def get_total_feedback(self, session):
        """ returns total amount of yes feedbacks """

        feedbacks = session.query(Feedback).count()

        return feedbacks

    @local_session
    def get_avg_rate_feedback_yes(self, session):
        """ returns average rate of total feedbacks yes """
        feedbacks_yes = (
            session.query(Feedback)
            .filter(Feedback.rate != None, Feedback.conversation_occured == True)
            .all()
        )
        total_rate = 0
        amount_feedbacks = 0
        for feedback in feedbacks_yes:
            total_rate += feedback.rate
            amount_feedbacks += 1

        return round(total_rate / amount_feedbacks, 1)

    @local_session
    def ban_user(self, session, chat_id: int) -> None:
        """ user banned the bot """

        user = session.query(User).filter(User.chat_id == chat_id).first()
        if user and user.is_banned is False:
            user.is_banned = True
            session.commit()

    @local_session
    def unban_user(self, session, chat_id: int) -> None:
        """ user started conversation after ban """

        user = session.query(User).filter(User.chat_id == chat_id).first()
        if user.is_banned is True:
            user.is_banned = False
            session.commit()

    @local_session
    def ban_users(self, session, failed_users: Dict[int, dict]) -> None:
        """ set User.is_banned to true and log banned as Action"""

        if failed_users:
            ban_id = session.query(Action.id).filter(Action.name == "ban").first()
            chat_ids = list(failed_users.keys())

            users = session.query(User).filter(User.chat_id.in_(chat_ids)).all()
            for user in users:
                is_banned, error = failed_users[user.chat_id]
                if not is_banned:
                    print(error)
                    user.is_banned = True
                    # create action in case user banned for the first time
                    new_action = UserAction(user_id=user.id, action=ban_id[0])
                    # log banned time
                    session.add(new_action)
            session.commit()

    @local_session
    def unban_users(self, session, chat_ids: List[int]) -> None:
        """ set User.is_banned to flase"""

        if chat_ids:
            users = session.query(User).filter(User.chat_id.in_(chat_ids)).all()
            for user in users:
                if user.is_banned:
                    user.is_banned = False  # change user field
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
                    new_action = UserAction(user_id=user.id, action=ban_id)
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
        user = self.get_user_data(chat_id)
        new_action = UserAction(user_id=user.id, action=action_id)
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
