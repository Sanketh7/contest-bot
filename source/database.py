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

async def set_user_class_select_dialog(contest_index, user_id, dialog_id):
    db.reference("contest_"+str(contest_index)).child("user_to_class_select_dialog").child(str(user_id)).set(dialog_id)
    db.reference("contest_"+str(contest_index)).child("class_select_dialog_to_user").child(str(dialog_id)).set(user_id)

async def get_class_select_dialog(contest_index, user_id):
    # remember to check if it's none
    return db.reference("contest_"+str(contest_index)).child("user_to_class_select_dialog").child(str(user_id)).get()

async def delete_user_class_select_dialog(contest_index, user_id):
    try:
        dialog_id = db.reference("contest_"+str(contest_index)).child("user_to_class_select_dialog").child(str(user_id)).get()
        db.reference("contest_"+str(contest_index)).child("user_to_class_select_dialog").child(str(user_id)).delete()
        db.reference("contest_"+str(contest_index)).child("class_select_dialog_to_user").child(str(dialog_id)).delete()
    except:
        print("Failed to delete dialog from database.")

async def set_user_submission_dialog(contest_index, user_id, dialog_id):
    db.reference("contest_"+str(contest_index)).child("user_to_submission_dialog").child(str(user_id)).set(dialog_id)
    db.reference("contest_"+str(contest_index)).child("submission_dialog_to_user").child(str(dialog_id)).set(user_id)

async def get_submission_dialog(contest_index, user_id):
    # remember to check if it's none
    return db.reference("contest_"+str(contest_index)).child("user_to_submission_dialog").get()