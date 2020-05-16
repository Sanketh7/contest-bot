import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import uuid

def init_database():
    cred = credentials.Certificate("db-key.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://contest-bot-test.firebaseio.com"
    })

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

async def get_all_metadata():
    ret = db.reference("meta_data").get()
    if ret is None:
        ret = {}
    return ret

async def get_points_document(contest_type):
    return db.reference("points_documents").child(str(contest_type)).get()

async def set_points_document(contest_type, url):
    db.reference("points_documents").child(str(contest_type)).set(str(url))

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

async def add_submission_to_user(contest_id, user_id, post_id, submission_data: dict):
    db.reference("contest_"+str(contest_id)).child("submissions").child(str(user_id)).set(submission_data)

    prev_post = db.reference("contest_"+str(contest_id)).child("user_to_verification").child(str(user_id)).get()

    db.reference("contest_"+str(contest_id)).child("verification_to_user").child(str(post_id)).set(user_id)
    db.reference("contest_"+str(contest_id)).child("user_to_verification").child(str(user_id)).set(post_id)

    return prev_post

async def get_user_from_verification(post_id, contest_id):
    # check to make sure it's not None
    return db.reference("contest_"+str(contest_id)).child("verification_to_user").child(str(post_id)).get()

async def accept_submission(contest_id, post_id):
    user_id = db.reference("contest_"+str(contest_id)).child("verification_to_user").child(str(post_id)).get()
    if user_id is None:
        return

    submission = db.reference("contest_"+str(contest_id)).child("submissions").child(str(user_id)).get()
    if submission is None:
        return

    db.reference("contest_" + str(contest_id)).child("accepted").child(str(user_id)).set(submission)
    db.reference("leaderboard").child(str(user_id)).set({
        "points": submission["points"],
        "class": submission["class"]
    })

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

async def add_submission_count(contest_id, user_id):
    old_value = db.reference("contest_" + str(contest_id)).child("user_to_submission_count").child(str(user_id)).get()
    if old_value is None:
        old_value = 0
    db.reference("contest_" + str(contest_id)).child("user_to_submission_count").child(str(user_id)).set(old_value+1)
    return old_value+1

async def allowed_to_submit(contest_id, user_id):
    val = db.reference("contest_" + str(contest_id)).child("user_to_submission_count").child(str(user_id)).get()
    if val is None:
        val = 0
    return val < 5