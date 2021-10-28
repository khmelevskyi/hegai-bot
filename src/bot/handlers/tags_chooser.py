""" class to contain push data """
from typing import Dict
from typing import List

from ..db_functions import db_session


class TagsChooser:
    """ container for data to be pushed """

    def __init__(self):
        self.user_tags_dict: Dict[str, List[str]] = {}
        self._page: int = 0
        self._page_tags = []
        self._statuses = []
        self._curr_status: str = None
        self._status_tags = []

    @property
    def statuses(self):
        """ user tags statuses """
        return self._statuses

    @statuses.setter
    def statuses(self, statuses):
        self._statuses = statuses
        self._curr_status = statuses[0]

    @property
    def curr_status(self):
        """ current status in statuses """
        return self._curr_status

    @curr_status.setter
    def curr_status(self, data: str):
        idx = self._statuses.index(self._curr_status)
        if data == "category_n":
            self._curr_status = self._statuses[idx + 1]
            print(self._curr_status)

    @property
    def status_tags(self):
        """ tags of one status """
        return self._status_tags

    @status_tags.setter
    def status_tags(self, curr_status):
        self._status_tags = db_session.get_tags_by_status(curr_status)

    @property
    def page(self) -> int:
        """button"""
        return self._page

    @page.setter
    def page(self, data: str):
        """ create button """
        if data == "back":
            self._page = self._page - 10
        elif data == "next":
            self._page = self._page + 10
        else:
            self._page = 0

    @property
    def page_tags(self):
        """ tags of one page """
        status_tags = self._status_tags
        page = self._page
        self._page_tags = status_tags[page : page + 8]
        return self._page_tags

    def flush(self):
        """ clean function """
        self.user_tags_dict: Dict[str, List[str]] = {}
        self.page: int = 0
        self._page_tags = []
        self._statuses = []
        self._curr_status: str = None
        self._status_tags = []
