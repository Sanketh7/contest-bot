import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import uuid
from util import Logger
import dataset


class Database:
    '''
    def init_database():
        cred = credentials.Certificate("../db-key.json")
        firebase_admin.initialize_app(cred, {
            "databaseURL": "https://contest-bot-test.firebaseio.com/"
        })
    '''
    db: dataset.Database

    @staticmethod
    def init_database(url: str):
        Database.db = dataset.connect(url)

    '''
    async def new_contest(contest_type, end_time, post_id):
        meta_data = db.reference("meta_data")
    
        # update index of current contest
        last_index = meta_data.child("current_contest_index").get()
        if last_index is None:
            last_index = 0
    
        new_data = {
            "current_contest_index": last_index+1,
            "is_contest_active": True,
            "current_contest_type": str(contest_type),
            "current_contest_end_time": end_time,
            "current_contest_post_id": post_id,
            "current_points_document": await get_points_document(contest_type)
        }
        meta_data.update(new_data)
        return new_data
    '''
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

        ref.update(dict(
            name="main",
            current_contest_index=new_data["current_contest_index"],
            is_contest_active=new_data["is_contest_active"],
            current_contest_type=new_data["current_contest_type"],
            current_contest_end_time=new_data["current_contest_end_time"],
            current_contest_post_id=new_data["current_contest_post_id"],
            current_points_document=new_data["current_points_document"]
        ))

    '''
    async def get_all_metadata():
        ret = db.reference("meta_data").get()
        if ret is None:
            ret = {}
        return ret
    '''
    @staticmethod
    def get_all_metadata():
        ref: dataset.Table = Database.db["meta_data"]
        data = ref.find_one()
        if data is None:
            return {}

        col = ref.columns
        ret = {}
        for key in col:
            ret[key] = data[key]
        return ret


    '''
    async def get_points_document(contest_type):
        return db.reference("points_documents").child(str(contest_type)).get()
    '''
    @staticmethod
    def get_points_document(contest_type):
        pass

    '''
    async def set_points_document(contest_type, url):
        db.reference("points_documents").child(str(contest_type)).set(str(url))
    
    '''
    @staticmethod
    def set_points_document(contest_type, url):
        pass

    '''
    async def end_contest():
        meta_data = db.reference("meta_data")
        new_data = {
            "current_contest_index": meta_data.child("current_contest_index").get(),
            "is_contest_active": False,
            "current_contest_type": "",
            "current_contest_end_time": -1,
            "current_contest_post_id": -1,
            "current_points_document": ""
        }
        meta_data.update(new_data)
        return new_data
    '''
    @staticmethod
    def end_contest():
        ref: dataset.Table = Database.db["meta_data"]
        old_data = ref.find_one()
        if old_data is None:
            Database.reset_meta_data()
            old_data = ref.find_one()

        new_data = {
            "current_contest_index": old_data["current_contest_index"],
            "is_current_contest_active": False,
            "current_contest_type": "",
            "current_contest_end_time": -1,
            "current_contest_post_id": -1,
            "current_points_document": ""
        }


'''
async def reset_meta_data():
    meta_data = db.reference("meta_data")
    new_data = {
        "current_contest_index": 0,
        "is_contest_active": False,
        "current_contest_type": "",
        "current_contest_end_time": -1,
        "current_contest_post_id": -1,
        "current_points_document": ""
    }
    meta_data.update(new_data)

async def create_character(contest_id, user_id, character_class: str):
    contest = db.reference("contest_" + str(contest_id))
    contest.child("characters").child(str(user_id)).set({
        "class": str(character_class),
        "keywords": [],
        "points": 0,
    })

async def get_character(contest_id, user_id):
    contest = db.reference("contest_" + str(contest_id))
    return contest.child("characters").child(str(user_id)).get()

async def has_current_character(contest_id, user_id):
    contest = db.reference("contest_" + str(contest_id))
    data = contest.child("characters").child(str(user_id)).get()
    if data is None:
        return False
    else:
        return True

async def add_pending_submission(contest_id, post_id, submission_data: dict):
    contest = db.reference("contest_"+str(contest_id))
    contest.child("pending").child(str(post_id)).set(submission_data)

async def get_pending_submission_data(contest_id, post_id):
    contest = db.reference("contest_"+str(contest_id))
    return contest.child("pending").child(str(post_id)).get()

async def accept_pending_submission(contest_id, post_id, points_data, staff_user_id: int):
    contest = db.reference("contest_"+str(contest_id))

    submission_data = contest.child("pending").child(str(post_id)).get()
    if submission_data is None:
        return
    user_id = submission_data["user"]
    if user_id is None:
        return

    # move this submission to accepted
    contest.child("accepted").child(str(post_id)).set(submission_data)

    old_character_data = contest.child("characters").child(str(user_id)).get()
    if old_character_data is None or old_character_data["class"] != submission_data["class"]:
        await create_character(contest_id, user_id, submission_data["class"])

    # do this to remove duplicates
    if "keywords" not in old_character_data:
        old_character_data["keywords"] = set()
    if "keywords" not in submission_data:
        submission_data["keywords"] = set()

    new_keywords = set(old_character_data["keywords"]).union(set(submission_data["keywords"]))

    new_points = 0
    for item in new_keywords:
        new_points += points_data[item][submission_data["class"]]

    contest.child("characters").child(str(user_id)).update({
        "points": new_points,
        "keywords": list(new_keywords)
    })

    db.reference("leaderboard").child(str(user_id)).set({
        "points": int(new_points),
        "class": str(old_character_data["class"])
    })

    contest.child("pending").child(str(post_id)).delete()

    await Logger.accepted_submission(staff_user_id, user_id, submission_data)

    return user_id

async def get_user_from_verification(contest_id, post_id):
    contest = db.reference("contest_" + str(contest_id))

    submission_data = contest.child("pending").child(str(post_id)).get()
    if submission_data is None:
        return
    user_id = submission_data["user"]
    if user_id is None:
        return
    return user_id

async def get_top_users(count):
    return db.reference("leaderboard").order_by_child("points").limit_to_last(count).get()

async def replace_leaderboard(new_post_id):
    # check to make sure it's not None
    old_id = db.reference("leaderboard_id").get()
    db.reference("leaderboard_id").set(new_post_id)
    return old_id

async def clear_leaderboard():
    db.reference("leaderboard").delete()

async def schedule_contest(contest_type, start_time, end_time):
    uid = uuid.uuid4().hex[:8]
    data = {
        "contest_type": str(contest_type),
        "start_time": float(start_time),
        "end_time": float(end_time)
    }
    new_contest_ref = db.reference("scheduled_contests").child(str(uid))
    new_contest_ref.set(data)
    return {
        "key": str(uid),
        "data": data
    }

async def get_scheduled_contest_list():
    return db.reference("scheduled_contests").get()

async def remove_contest_with_id(contest_id: str):
    db.reference("scheduled_contests").child(contest_id).delete()
'''