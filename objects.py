from database import DB
from pony.orm import Entity, PrimaryKey, Required, Optional, time, StrArray, Set
from datetime import datetime
from points_manager import PointsManager
import typing


class Contest(DB.db.Entity):
    id = PrimaryKey(int, auto=True)
    is_active = Required(bool)
    start_time = Required(datetime)
    end_time = Required(datetime)
    post_id = Optional(int)

    characters = Set('Character')


class Character(DB.db.Entity):
    id = PrimaryKey(int, auto=True)
    user_id = Required(int)

    is_active = Required(bool)
    is_banned = Required(bool)

    rotmg_class = Required(str)
    keywords = Required(StrArray)

    submissions = Set('Submission')
    contest = Required(Contest)

    @classmethod
    def get_active_character(cls, user_id):
        return cls.select(lambda c: c.is_active and c.user_id == user_id).first()

    @property
    def points(self):
        kw_set = set(self.keywords)
        points = 0
        for kw in kw_set:
            points += PointsManager.points_data[kw][self.rotmg_class]
        return points

    def keywords_intersection(self, new_kw: set[str]) -> set[str]:
        kw = set(self.keywords)
        return kw.intersection(new_kw)

    def delta_keywords(self, new_kw: set[str]) -> set[str]:
        kw_set = set(self.keywords)
        return new_kw.difference(kw_set)

    def delta_points(self, new_kw: set[str]) -> int:
        delta_kw = self.delta_keywords(new_kw)
        delta_points = 0
        for kw in delta_kw:
            points += PointsManager.points_data[kw][self.rotmg_class]
        return delta_points


class Submission(DB.db.Entity):
    id = PrimaryKey(int, auto=True)
    character = Required(Character)

    is_accepted = Required(bool)

    post_id = Required(int)

    keywords = Required(StrArray)
    img_url = Required(str)

    @ property
    def points(self):
        kw_set = set(self.keywords)
        points = 0
        for kw in kw_set:
            points += PointsManager.points_data[kw][self.character.rotmg_class]
        return points
