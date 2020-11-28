from source.database.db_objects import *
import discord
from datetime import datetime
from source.cache import Cache
from source.points_data import PointsDataManager
from source.payloads import *
from typing import List


class DB:
    db: Database

    """''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''                    
    
                        INIT
    
    """''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    @staticmethod
    def init_database(url: str) -> bool:
        # Database.db = dataset.connect(url)
        DB.db = Database()
        DB.db.bind(provider='sqlite', filename=url, create_db=True)
        DB.db.generate_mapping(create_tables=True)

        return True

    @staticmethod
    @db_session
    def update_cache() -> bool:
        contest = Contest.select(lambda c: c.is_active).first()
        if contest:
            Cache.contest_id = contest.id
            Cache.contest_post_id = contest.post_id
            Cache.contest_end_time = contest.end_time
            Cache.is_contest_active = contest.is_active
            Cache.contest_points_document_url = contest.contest_type.points_document_url

        return True

    """''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    
                        SCHEDULE AND CONTEST MANAGEMENT
    
    """''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    @staticmethod
    @db_session
    def check_scheduled_contest() -> bool:
        curr_time = datetime.utcnow().timestamp()
        contest = Contest.select(lambda c: c.start_time <= curr_time <= c.end_time and not c.is_active).first()
        if not contest:
            return False
        return True

    @staticmethod
    @db_session
    def check_and_activate_scheduled_contest(post_id: int) -> bool:
        curr_time = datetime.utcnow().timestamp()
        contest = Contest.select(lambda c: c.start_time <= curr_time <= c.end_time and not c.is_active).first()
        if not contest:
            return False

        contest.activate(post_id)
        Cache.reload()

        return True

    @staticmethod
    @db_session
    def check_and_deactivate_current_contest() -> bool:
        contest = Contest.select(lambda c: c.id == Cache.contest_id).first()
        if not contest or not Cache.is_contest_active:
            return False

        contest.deactivate()
        Cache.reload()

        return True

    @staticmethod
    @db_session
    def add_contest_to_schedule(contest_type: str, start_time: float, end_time: float) -> bool:
        Contest(
            type=contest_type,
            start_time=start_time,
            end_time=end_time,
            post_id=None,  # assigned when contest is activated
            is_active=False,
            # contestants is an empty set
        )

        return True

    @staticmethod
    @db_session
    def remove_contest_from_schedule(contest_id: int) -> bool:
        contest: Contest = Contest.select(lambda c: c.id == contest_id).first()
        if not contest:
            return False

        contest.delete()

        return True

    @staticmethod
    @db_session
    def get_scheduled_contests() -> List[ContestPayload]:
        curr_time = datetime.utcnow().timestamp()
        contests = Contest.select(lambda c: not c.is_active and c.start_time >= curr_time).order_by(
            desc(Contest.start_time))

        ret = []
        for contest in contests:
            ret.append(ContestPayload(
                id=contest.id,
                contest_type_name=contest.contest_type.name,
                start_time=contest.start_time,
                end_time=contest.end_time,
                post_id=contest.post_id,
                is_active=contest.is_active()
            ))
        return ret

    """''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    
                        CONTESTANT MANAGEMENT
    
    """''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    @staticmethod
    @db_session
    def register_contestant(user: discord.User) -> bool:
        contestant = Contestant.select(lambda c: c.user_id == user.id and c.contest.id == Cache.contest_id).first()
        if not contestant:
            return False

        contest: Contest = Contest.select(lambda c: c.id == Cache.contest_id and c.is_active).first()
        if not contest:
            return False

        Contestant(
            contest=contest,
            user_id=user.id,
            # characters = empty set
            active_character=None,
            # submissions = empty set
            is_banned=False
        )

        return True

    @staticmethod
    @db_session
    def ban_contestant(user: discord.User) -> bool:
        if not Cache.is_contest_active:
            return False

        contestant: Contestant = Contestant.select(
            lambda c: c.user_id == user.id and c.contest.id == Cache.contest_id).first()
        if not contestant:
            return False

        contestant.is_banned = True

        return True

    @staticmethod
    @db_session
    def unban_contestant(user: discord.User) -> bool:
        if not Cache.is_contest_active:
            return False

        contestant: Contestant = Contestant.select(
            lambda c: c.user_id == user.id and c.contest.id == Cache.contest_id).first()
        if not contestant:
            return False

        contestant.is_banned = False

        return True

    @staticmethod
    @db_session
    def is_contestant_banned(user: discord.User) -> bool:
        if not Cache.is_contest_active:
            return False

        contestant: Contestant = Contestant.select(
            lambda c: c.user_id == user.id and c.contest.id == Cache.contest_id).first()
        if not contestant:
            return False

        return contestant.is_banned

    @staticmethod
    @db_session
    def get_ban_list() -> List[ContestantPayload]:
        if not Cache.is_contest_active:
            return []

        banned = Contestant.select(lambda c: c.is_banned and c.contest.id == Cache.contest_id)
        ret = []
        for contestant in banned:
            ret.append(ContestantPayload(
                user_id=contestant.user_id,
                is_banned=contestant.is_banned
            ))
        return ret

    """''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    
                        CONTEST TYPE MANAGEMENT
    
    """''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    @staticmethod
    @db_session
    def set_points_document_url(contest_type: str, new_url: str) -> bool:
        contest_type_data: ContestType = ContestType.select(lambda ct: ct.contest_type == contest_type).first()
        if not contest_type_data:
            return False

        contest_type_data.points_document_url = new_url
        Cache.reload()

        return True

    """''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    
                        CHARACTER MANAGEMENT                    
    
    """''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    @staticmethod
    @db_session
    def create_character(user: discord.User, rotmg_class: str) -> bool:
        contestant: Contestant = Contestant.select(lambda c: c.user_id == user.id and c.contest.id == Cache.contest_id)
        if not contestant:
            return False

        contest: Contest = Contest.select(lambda c: c.id == Cache.contest_id and c.is_active).first()
        if not contest:
            return False

        character: Character = Character(
            contest=contest,
            contestant=contestant,
            rotmg_class=rotmg_class,
            keywords=[],
            points=0
        )

        contestant.characters.add(character)
        contestant.active_character = character

        return True

    @staticmethod
    @db_session
    def get_current_character(user: discord.User):
        contestant: Contestant = Contestant.select(lambda c: c.user_id == user.id and c.contest.id == Cache.contest_id).first()
        if not contestant:
            return None

        character: Character = contestant.active_character
        if not character:
            return None

        return character  # TODO: make CharacterPayload

    @staticmethod
    @db_session
    def remove_character_keywords(character_id: int, keywords: set):
        character: Character = Character.select(lambda c: c.id == character_id).first()
        if not character:
            return False

        new_keywords = set(character.keywords)
        for item in new_keywords:
            if item in keywords:
                new_keywords.remove(item)

        new_points = PointsDataManager.calculate_points(new_keywords)

        # TODO add logging where this method is called

        character.keywords = new_keywords
        character.points = new_points

        return True

    @staticmethod
    @db_session
    def add_character_keywords(character_id: int, keywords: set):
        character: Character = Character.select(lambda c: c.id == character_id).first()
        if not character:
            return False

        new_keywords = set(character.keywords)
        new_keywords.union(keywords)

        new_points = PointsDataManager.calculate_points(new_keywords)

        # TODO add logging where this method is called

        character.keywords = new_keywords
        character.points = new_points

        return True

    @staticmethod
    @db_session
    def get_user_characters(user: discord.User):
        contestant: Contestant = Contestant.select(
            lambda c: c.user_id == user.id and c.contest.id == Cache.contest_id).first()
        if not contestant:
            return None

        ret = []
        for character in contestant.characters:
            ret.append(CharacterPayload(
                id=character.id,
                user_id=character.contestant.user_id,
                rotmg_class=character.rotmg_class,
                keywords=set(character.keywords),
                points=character.points,
                is_active=character.is_active()
            ))

        return ret

    @staticmethod
    @db_session
    def get_top_characters(top_count: int):
        characters = Character.select(lambda c: c.contest.id == Cache.contest_id).order_by(desc(Character.points))[
                     :top_count]

        ret = []
        for character in characters:
            ret.append(CharacterPayload(
                id=character.id,
                user_id=character.contestant.user_id,
                rotmg_class=character.rotmg_class,
                keywords=set(character.keywords),
                points=character.points,
                is_active=character.is_active()
            ))
        return ret

    """''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    
                        SUBMISSION MANAGEMENT
    
    """''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    @staticmethod
    @db_session
    def add_pending_submission(user: discord.User, post_id: int, keywords: set, points: int, image_url: str):
        if not Cache.is_contest_active:
            return False

        contest: Contest = Contest.select(lambda c: c.id == Cache.contest_id and c.is_active).first()
        if not contest:
            return False

        # get current character
        character: Character = DB.get_current_character(user)
        if not character:
            return False

        Submission(
            contest=contest,
            is_pending=True,
            is_accepted=None,
            post_id=post_id,
            character=character,
            keywords=list(keywords),
            points=points,
            image_url=image_url
        )

        return True

    @staticmethod
    @db_session
    def accept_submission(post_id: int):
        submission: Submission = Submission.select(lambda s: s.post_id == post_id).first()
        if not submission:
            return False

        new_keywords = set(submission.keywords)
        old_keywords = set(submission.character.keywords)

        total_keywords = new_keywords.union(old_keywords)

        new_points = PointsDataManager.calculate_points(total_keywords)

        submission.is_pending = False
        submission.is_accepted = True
        submission.character.keywords = list(total_keywords)
        submission.points = new_points
        # TODO: add logging where this method is called
        return True
