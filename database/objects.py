from pony.orm import PrimaryKey, Required, Optional, StrArray, Set, Database
from datetime import datetime
from points import PointsManager
import typing

db = Database()
db.bind(provider='sqlite', filename='database.db', create_db=True)


class Contest(db.Entity):
    id = PrimaryKey(int, auto=True)
    is_active = Required(bool)
    start_time = Required(datetime)
    end_time = Required(datetime)
    post_id = Optional(int, size=64)

    # contains strings of user IDs (pony.orm doesn't support 64bit IntArray)
    banned_users = Required(StrArray)

    characters = Set('Character')

    @property
    def should_end(self):
        time_now = datetime.now()
        return time_now >= self.end_time

    @classmethod
    def get_current_contest(cls):
        return cls.select(lambda c: c.is_active).first()

    @classmethod
    def get_ready_contest(cls):
        time_now = datetime.now()
        if cls.get_current_contest():
            return None
        return cls.select(lambda c: c.start_time <= time_now <= c.end_time).first()

    @classmethod
    def contests_after_datetime(cls, dt: datetime):
        return cls.select(lambda c: c.start_time < dt)


class Character(db.Entity):
    id = PrimaryKey(int, auto=True)
    user_id = Required(int, size=64)

    is_active = Required(bool)

    rotmg_class = Required(str)
    keywords = Required(StrArray)

    submissions = Set('Submission')
    contest = Required(Contest)

    @property
    def points(self):
        kw_set = set(self.keywords)
        points = 0
        for kw in kw_set:
            points += PointsManager.points_data[kw][self.rotmg_class]
        return points

    @classmethod
    def get_active_character(cls, contest_id: int, user_id: int):
        return cls.select(lambda c: c.is_active and c.user_id == user_id and c.contest.id == contest_id).first()

    @classmethod
    def get_all_characters(cls, contest_id: int):
        return list(cls.select(lambda c: c.contest.id == contest_id and str(c.user_id) not in c.contest.banned_users[:]))

    @classmethod
    def get_characters_by_user(cls, contest_id: int, user_id: int):
        return cls.select(lambda c: c.contest.id == contest_id and c.user_id == user_id)

    def keywords_intersection(self, new_kw: typing.Set[str]) -> typing.Set[str]:
        kw = set(self.keywords)
        return kw.intersection(new_kw)

    def delta_keywords(self, new_kw: typing.Set[str]) -> typing.Set[str]:
        kw_set = set(self.keywords)
        return new_kw.difference(kw_set)

    def delta_points(self, new_kw: typing.Set[str]) -> int:
        delta_kw = self.delta_keywords(new_kw)
        delta_points = 0
        for kw in delta_kw:
            delta_points += PointsManager.points_data[kw][self.rotmg_class]
        return delta_points


class Submission(db.Entity):
    id = PrimaryKey(int, auto=True)
    character = Required(Character)

    is_accepted = Required(bool)

    post_id = Required(int, size=64)

    keywords = Required(StrArray)
    img_url = Required(str)

    @classmethod
    def get_from_post_id(cls, post_id: int):
        return cls.select(lambda c: c.post_id == post_id).first()

    @property
    def points(self):
        kw_set = set(self.keywords)
        points = 0
        for kw in kw_set:
            points += PointsManager.points_data[kw][self.character.rotmg_class]
        return points


db.generate_mapping(create_tables=True)
