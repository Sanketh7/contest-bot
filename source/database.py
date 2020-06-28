import uuid
from util import Logger
import dataset
import json

class Database:
    db: dataset.Database

    @staticmethod
    def init_database(url: str):
        Database.db = dataset.connect(url)

    @staticmethod
    def new_contest(contest_type, end_time, post_id):
        ref: dataset.Table = Database.db["meta_data"]
        old_data = ref.find_one()

        if old_data is None:
            Database.reset_meta_data()
            old_data = ref.find_one()

        new_data = {
            "current_contest_index": old_data["current_contest_index"] + 1,
            "is_contest_active": True,
            "current_contest_type": str(contest_type),
            "current_contest_end_time": end_time,
            "current_contest_post_id": post_id,
            "current_points_document": Database.get_points_document(contest_type)
        }

        ref.upsert(dict(
            name="main",
            current_contest_index=new_data["current_contest_index"],
            is_contest_active=new_data["is_contest_active"],
            current_contest_type=new_data["current_contest_type"],
            current_contest_end_time=new_data["current_contest_end_time"],
            current_contest_post_id=new_data["current_contest_post_id"],
            current_points_document=new_data["current_points_document"]
        ), ["name"])

        return new_data

    @staticmethod
    def get_all_metadata():
        ref: dataset.Table = Database.db["meta_data"]
        data = ref.find_one(name="main")
        if data is None:
            return None

        col = ref.columns
        ret = {}
        for key in col:
            ret[key] = data[key]
        return ret

    @staticmethod
    def get_points_document(contest_type):
        ref: dataset.Table = Database.db["contest_type_data"]
        data = ref.find_one(contest_type="ppe")
        if data is None:
            return ""
        return str(data["points_document"])

    @staticmethod
    def set_points_document(contest_type, url):
        ref: dataset.Table = Database.db["contest_type_data"]
        data = dict(contest_type=contest_type, points_document=url)
        ref.upsert(data, ["contest_type"])

    @staticmethod
    def end_contest():
        ref: dataset.Table = Database.db["meta_data"]
        old_data = ref.find_one()
        if old_data is None:
            Database.reset_meta_data()
            old_data = ref.find_one()

        new_data = {
            "current_contest_index": old_data["current_contest_index"],
            "is_contest_active": False,
            "current_contest_type": "",
            "current_contest_end_time": -1,
            "current_contest_post_id": -1,
            "current_points_document": ""
        }

        ref.upsert(dict(
            name="main",
            current_contest_index=new_data["current_contest_index"],
            is_contest_active=new_data["is_contest_active"],
            current_contest_type=new_data["current_contest_type"],
            current_contest_end_time=new_data["current_contest_end_time"],
            current_contest_post_id=new_data["current_contest_post_id"],
            current_points_document=new_data["current_points_document"]
        ), ["name"])

        return new_data

    @staticmethod
    def reset_meta_data():
        Database.db["meta_data"].drop()
        ref: dataset.Table = Database.db["meta_data"]

        new_data = {
            "current_contest_index": 0,
            "is_contest_active": False,
            "current_contest_type": " ",
            "current_contest_end_time": -1,
            "current_contest_post_id": -1,
            "current_points_document": " "
        }

        ref.upsert(dict(
            name="main",
            current_contest_index=new_data["current_contest_index"],
            is_contest_active=new_data["is_contest_active"],
            current_contest_type=new_data["current_contest_type"],
            current_contest_end_time=new_data["current_contest_end_time"],
            current_contest_post_id=new_data["current_contest_post_id"],
            current_points_document=new_data["current_points_document"]
        ), ["name"])

        return new_data

    @staticmethod
    def create_character(contest_id, user_id, character_class: str):
        ref: dataset.Table = Database.db["contest_" + str(contest_id) + "_characters"]
        old_chars = ref.find(user_id=int(user_id))
        for row in old_chars:
            row["is_active"] = False
            ref.upsert(row, ["id"])

        serial_keywords = json.dumps([])
        new_data = dict({
            "user_id": int(user_id),
            "character_id": str(uuid.uuid4().hex),
            "class": str(character_class),
            "keywords": serial_keywords,
            "points": 0,
            "is_active": True
        })
        ref.insert(new_data)

    @staticmethod
    def get_character(contest_id, user_id):
        ref: dataset.Table = Database.db["contest_" + str(contest_id) + "_characters"]
        curr_char = ref.find_one(user_id=int(user_id), is_active=True)
        if curr_char is None:
            return None
        return dict({
            "class": str(curr_char["class"]),
            "keywords": json.loads(curr_char["keywords"]),
            "points": int(curr_char["points"]),
        })

    @staticmethod
    def has_current_character(contest_id, user_id):
        ref: dataset.Table = Database.db["contest_" + str(contest_id) + "_characters"]
        curr_char = ref.find_one(user_id=str(user_id), is_active=True)
        if curr_char is None:
            return False
        else:
            return True

    @staticmethod
    def update_character(contest_id, character_id, keywords, points):
        pass

    @staticmethod
    def get_uuid_of_current_character(contest_id, user_id):
        ref: dataset.Table = Database.db["contest_" + str(contest_id) + "_characters"]
        curr_char = ref.find_one(user_id=int(user_id), is_active=True)
        if curr_char is None:
            return None
        return curr_char["character_id"]

    @staticmethod
    def add_pending_submission(contest_id, post_id, user_id, class_str, keywords, points, img_url):
        ref: dataset.Table = Database.db["contest_" + str(contest_id) + "_pending"]
        # get uuid of current character
        curr_uuid = Database.get_uuid_of_current_character(contest_id, user_id)
        if curr_uuid is None:
            return
        serial_keywords = json.dumps(list(keywords))
        ref.insert(dict({
            "post_id": str(post_id),
            "character_id": str(curr_uuid),
            "user_id": int(user_id),
            "class": str(class_str),
            "keywords": serial_keywords,
            "points": int(points),
            "img_url": str(img_url)
        }))

    @staticmethod
    def get_pending_submission_data(contest_id, post_id):
        ref: dataset.Table = Database.db["contest_" + str(contest_id) + "_pending"]
        data = ref.find_one(post_id=str(post_id))
        return dict({
            "user_id": int(data["user_id"]),
            "class": str(data["class"]),
            "keywords": json.loads(data["keywords"]),
            "points": int(data["points"]),
            "img_url": str(data["img_url"])
        })

    @staticmethod
    async def accept_pending_submission(contest_id, post_id, points_data, staff_user_id: int):
        ref_pending: dataset.Table = Database.db["contest_" + str(contest_id) + "_pending"]
        submission_data = ref_pending.find_one(post_id=str(post_id))
        if submission_data is None:
            return
        user_id = submission_data["user_id"]
        if user_id is None:
            return

        # move this to accepted
        ref_accepted: dataset.Table = Database.db["contest_" + str(contest_id) + "_accepted"]
        ref_accepted.insert_ignore(dict({
            "post_id": str(submission_data["post_id"]),
            "character_id": str(submission_data["character_id"]),
            "user_id": int(submission_data["user_id"]),
            "class": str(submission_data["class"]),
            "keywords": submission_data["keywords"],
            "points": int(submission_data["points"]),
            "img_url": str(submission_data["img_url"])
        }), ["post_id"])

        ref_characters: dataset.Table = Database.db["contest_" + str(contest_id) + "_characters"]
        old_character_data = ref_characters.find_one(character_id=str(submission_data["character_id"]))

        new_keywords = set(json.loads(old_character_data["keywords"])).union(set(json.loads(submission_data["keywords"])))

        new_points = 0
        for item in new_keywords:
            new_points += points_data[item][submission_data["class"]]

        new_data = dict(
            character_id=str(submission_data["character_id"]),
            points=int(new_points),
            keywords=json.dumps(list(new_keywords))
        )

        ref_characters.upsert(new_data, ['character_id'])

        ref_pending.delete(post_id=str(submission_data["post_id"]))

        await Logger.accepted_submission(staff_user_id, user_id, submission_data)

        return user_id

    @staticmethod
    def get_user_from_verification(contest_id, post_id):
        ref: dataset.Table = Database.db["contest_" + str(contest_id) + "_pending"]
        submission_data = ref.find_one(post_id=str(post_id))
        if submission_data is None:
            return
        user_id = submission_data["user_id"]
        if user_id is None:
            return
        return user_id

    '''
    async def get_top_users(count):
        return db.reference("leaderboard").order_by_child("points").limit_to_last(count).get()
    '''
    @staticmethod
    def get_top_users(contest_id, count):
        ref: dataset.Table = Database.db["contest_" + str(contest_id) + "_characters"]
        ret = []  # dict of username, class, points
        for character in ref.all():
            ret.append({
                "user_id": character["user_id"],
                "class": character["class"],
                "points": character["points"]
            })
        ret = sorted(ret, key=lambda i: i["points"], reverse=True)
        ret = ret[:count]
        return ret

    '''
    async def replace_leaderboard(new_post_id):
        # check to make sure it's not None
        old_id = db.reference("leaderboard_id").get()
        db.reference("leaderboard_id").set(new_post_id)
        return old_id
    '''
    @staticmethod
    def replace_leaderboard_DEPRECATED(new_post_id):
        pass

    '''
    async def clear_leaderboard():
        db.reference("leaderboard").delete()
    '''
    @staticmethod
    def clear_leaderboard_DEPRECATED():
        pass

    @staticmethod
    def schedule_contest(contest_type, start_time, end_time):
        uid = uuid.uuid4().hex[:8]
        data = dict(
            schedule_id=str(uid),
            contest_type=str(contest_type),
            start_time=float(start_time),
            end_time=float(end_time)
        )
        ref: dataset.Table = Database.db["scheduled_contests"]
        ref.upsert(data, ["schedule_id"])
        return {
            "key": str(uid),
            "data": data
        }

    @staticmethod
    def get_scheduled_contest_list():
        ref: dataset.Table = Database.db["scheduled_contests"]
        data = ref.all()
        ret = dict()
        for contest in data:
            ret[contest["schedule_id"]] = dict(
                contest_type=str(contest["contest_type"]),
                start_time=float(contest["start_time"]),
                end_time=float(contest["end_time"])
            )
        if len(ret.keys()) == 0:
            return None
        return ret

    @staticmethod
    def remove_contest_with_id(contest_id: str):
        ref: dataset.Table = Database.db["scheduled_contests"]
        ref.delete(schedule_id=contest_id)