import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

def init_database():
    cred = credentials.Certificate("../db-key.json")
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
        "current_contest_index": meta_data.child("current_contest_index").get(),
        "is_contest_active": True,
        "current_contest_type": str(contest_type),
        "current_contest_end_time": end_time,
        "current_contest_post_id": post_id,
    }
    meta_data.update(new_data)
    return new_data;

async def get_all_metadata():
    ret = db.reference("meta_data").get()
    if ret is None:
        ret = {}
    return ret

async def end_contest():
    meta_data = db.reference("meta_data")
    new_data = {
        "current_contest_index": meta_data.child("current_contest_index").get(),
        "is_contest_active": False,
        "current_contest_type": "",
        "current_contest_end_time": -1,
        "current_contest_post_id": -1,
    }
    meta_data.update(new_data)
    return new_data

async def add_submission_to_user(contest_id, user_id, submission_data: dict):
    db.reference("contest_"+str(contest_id)).child("submissions").child(str(user_id)).set(submission_data)
    db.reference("contest_"+str(contest_id)).child("leaderboard").child(str(user_id)).set(submission_data["points"])