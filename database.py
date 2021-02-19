from objects import Contest, Character, Submission
from pony.orm import Database, db_session, select
from datetime import datetime
from settings import Settings


class DB:
    db: Database

    @staticmethod
    def init():
        DB.db = Database()
        DB.db.generate_mapping(create_tables=True)

    @staticmethod
    @db_session
    def schedule_contest(start_time: datetime, end_time: datetime):
        assert(end_time > start_time)
        Contest(
            is_active=False,
            start_time=start_time,
            end_time=end_time,
        )

    @staticmethod
    @db_session
    def remove_contest(id: int):
        Contest[id].delete()

    @staticmethod
    @db_session
    def new_character(contest_id: int, user_id: int, rotmg_class: str) -> None:
        assert(rotmg_class in Settings.rotmg_classes)
        contest = Contest[contest_id]
        if contest is None:
            return

        old_char = Character.get_active_character(user_id)
        if old_char:
            old_char.is_active = False

        Character(
            user_id=user_id,
            is_active=True,
            is_banned=False,
            rotmg_class=rotmg_class,
            keywords=[],
            points=0,
            contest=contest
        )

    @staticmethod
    @db_session
    def get_character(contest_id: int, user_id: int):
        contest = Contest[contest_id]
        if not contest:
            return None
        curr_char = Character.get_active_character(user_id)
        if not curr_char:
            return None
        return curr_char

    @staticmethod
    @db_session
    def add_submission(contest_id: int, user_id: int, post_id: int, rotmg_class: str, keywords: list[str], img_url: str):
        contest = Contest[contest_id]
        if not contest:
            return

        curr_char = Character.get_active_character(user_id)
        if not curr_char:
            return

        Submission(
            character=curr_char,
            is_accepted=False,
            post_id=post_id,
            keywords=keywords,
            img_url=img_url
        )
