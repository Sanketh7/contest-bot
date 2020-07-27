from pony.orm import *
from database.database import DB


class Contest(DB.db.Entity):
    id = PrimaryKey(int, auto=True)

    contest_type = Required('ContestType')
    start_time = Required(float)
    end_time = Required(float)
    post_id = Optional(int)
    is_active = Required(bool)

    @db_session
    def activate(self, post_id: int):
        self.is_active = True
        self.post_id = post_id

    @db_session
    def deactivate(self):
        self.is_active = False
        self.post_id = None


class ContestType(DB.db.Entity):
    name = Required(str)
    points_document_url = Required(str)


class Contestant(DB.db.Entity):
    contest = Required('Contest')

    user_id = Required(int)
    characters = Set('Character')
    active_character = Optional('Character')
    submissions = Set('Submission')
    is_banned = Required(bool)

    @property
    def has_current_character(self):
        return False if not self.active_character else True


class Character(DB.db.Entity):
    contest = Required('Contest')

    id = PrimaryKey(int, auto=True)
    contestant = Required('Contestant')
    rotmg_class = Required(str)
    keywords = Required(StrArray)
    points = Required(int)

    @property
    def is_active(self):
        return self is self.contestant.active_character

    @property
    def is_contestant_banned(self):
        return self.contestant.is_banned


class Submission(DB.db.Entity):
    contest = Required('Contest')

    id = PrimaryKey(int, auto=True)
    is_pending = Required(bool)
    is_accepted = Optional(bool)  # True if accepted, False if rejected, None if neither
    post_id = Required(int)
    character = Required('Character')
    keywords = Required(StrArray)
    points = Required(int)
    image_url = Required(str)