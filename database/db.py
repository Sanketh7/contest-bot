from database.objects import Contest, Character, Submission
from pony.orm import Database, db_session, select
from datetime import datetime
from settings import Settings


class DB:
    db: Database

    @staticmethod
    def init(db_file: str):
        DB.db = Database()
        DB.db.bind(provider='sqlite', filename=db_file, create_db=True)
        DB.db.generate_mapping(create_tables=True)

    @staticmethod
    @db_session
    def schedule_contest(start_time: datetime, end_time: datetime):
        assert(end_time > start_time)
        Contest(
            is_active=False,
            start_time=start_time,
            end_time=end_time,
            banned_users=set()
        )

    @staticmethod
    @db_session
    def remove_contest(id: int):
        if Contest[id]:
            Contest[id].delete()

    @staticmethod
    @db_session
    def get_contest_post_id():
        contest: Contest = DB.get_current_contest()
        if not contest:
            return None
        return contest.post_id

    @staticmethod
    @db_session
    def is_contest_running():
        return True if DB.get_current_contest() else False

    @staticmethod
    @db_session
    def get_current_contest():
        return Contest.get_current_contest()

    @staticmethod
    @db_session
    def get_current_contest_id():
        contest = DB.get_current_contest()
        return None if not contest else contest.id

    @staticmethod
    @db_session
    def get_schedule() -> list[Contest]:
        time_now = datetime.now()
        return list(Contest.contests_after_datetime(time_now))

    @staticmethod
    @db_session
    def get_ready_contest():
        return Contest.get_current_contest()

    @staticmethod
    @db_session
    def start_contest(contest_id: int, post_id: int):
        assert(not DB.get_current_contest())
        contest = Contest[contest_id]
        if contest:
            contest.post_id = post_id
            contest.is_active = True

    @staticmethod
    @db_session
    def end_current_contest():
        contest: Contest = DB.get_current_contest()
        assert(contest and contest.should_end)
        contest.is_active = False
        contest.post_id = None

    @staticmethod
    @db_session
    def change_end_time(end_time: datetime):
        contest: Contest = DB.get_current_contest()
        assert(contest and contest.is_active)
        contest.end_time = end_time

    @staticmethod
    @db_session
    def new_character(contest_id: int, user_id: int, rotmg_class: str) -> None:
        assert(rotmg_class in Settings.rotmg_classes)
        contest = Contest[contest_id]
        if not contest:
            return

        old_char = Character.get_active_character(contest_id, user_id)
        if old_char:
            old_char.is_active = False

        Character(
            user_id=user_id,
            is_active=True,
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
        curr_char = Character.get_active_character(contest_id, user_id)
        if not curr_char:
            return None
        return curr_char

    @staticmethod
    @db_session
    def get_characters_by_user(contest_id: int, user_id: int):
        query = Character.get_characters_by_user(contest_id, user_id)
        if not query:
            return []
        return list(query)

    @staticmethod
    @db_session
    def get_character_by_id(character_id: int):
        char: Character = Character[character_id]
        if not char:
            return None
        return char

    @staticmethod
    @db_session
    def get_top_characters(contest_id: int, count: int) -> list[Character]:
        contest: Contest = Contest[contest_id]
        if not contest:
            return []
        return list(Character.get_top_characters(contest_id, count))

    @staticmethod
    @db_session
    def add_submission(contest_id: int, user_id: int, post_id: int, keywords: list[str], img_url: str):
        contest = Contest[contest_id]
        if not contest:
            return

        curr_char = Character.get_active_character(contest_id, user_id)
        if not curr_char:
            return

        Submission(
            character=curr_char,
            is_accepted=False,
            post_id=post_id,
            keywords=keywords,
            img_url=img_url,
        )

    @staticmethod
    @db_session
    def accept_submission(post_id: int):
        submission = Submission.get_from_post_id(post_id)
        if not submission:
            return None
        assert(submission and not submission.is_accepted)

        old = set(submission.character.keywords)
        new = old.union(set(submission.keywords))
        submission.character.keywords = new
        submission.is_accepted = True

        return submission

    @staticmethod
    @db_session
    def get_submission(post_id: int):
        submission = Submission.get_from_post_id(post_id)
        if not submission:
            return None
        return submission

    @staticmethod
    @db_session
    def add_keywords(character_id: int, keywords: set[str]):
        char: Character = Character[character_id]
        if not char:
            return
        old = set(Character.keywords)
        new = old.union(keywords)
        char.keywords = list(new)

    @staticmethod
    @db_session
    def remove_keywords(character_id: int, keywords: set[str]):
        char: Character = Character[character_id]
        if not char:
            return

        old = set(Character.keywords)
        new = old.difference(keywords)
        char.keywords = list(new)

    @staticmethod
    @db_session
    def ban_user(contest_id: int, user_id: int):
        contest: Contest = Contest[contest_id]
        assert(contest)
        if user_id not in contest.banned_users:
            contest.banned_users.append(user_id)

    @staticmethod
    @db_session
    def unban_user(contest_id: int, user_id: int):
        contest: Contest = Contest[contest_id]
        assert(contest)
        contest.banned_users.remove(user_id)

    @staticmethod
    @db_session
    def get_ban_list(contest_id: int):
        contest: Contest = Contest[contest_id]
        assert(contest)
        return list(contest.banned_users)
