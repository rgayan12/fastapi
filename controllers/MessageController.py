from app.requests.UserEventRequest import UserEventRequest
from app.models import UserEventModel
from app.config.database import mongodb
from fastapi import HTTPException
from pymongo.errors import PyMongoError
from app.models.UserEventModel import UserEventModel
from app.service.MailChimpService import MailChimpService
from datetime import datetime, timedelta

userEventModel = UserEventModel()
mailChimpService = MailChimpService()


def handleUsersEvent(item: UserEventRequest):
    try:
        userEventModel.storeUserEvent(item)
        mailChimpService.syncContact(item)
        return {"message": "user synced"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Something went wrong")


async def getUsers():
    collections = mongodb.get_collection("user_events")
    users = collections.find()
    user_list = []
    for user in users:
        user['_id'] = str(user['_id'])  # Convert ObjectId to string
        user_list.append(user)
    return user_list


async def countEventRegistrations():
    try:
        collections = mongodb.get_collection("user_events")
        count = collections.count_documents({})
        return {"total_event_registrations": count}
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


async def countRecentRegistrations():
    try:
        collections = mongodb.get_collection("user_events")
        now = datetime.utcnow()
        past_24_hours = now - timedelta(days=1)
        count = collections.count_documents({"timestamp": {"$gte": past_24_hours}})
        return {"data": count}
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


async def getUserDataGroupedByMessage():
    try:
        pipeline = [
            {
                "$group": {
                    "_id": "$message",
                    "userData": {"$push": "$userData"}
                }
            }
        ]
        collection = mongodb.get_collection("user_events")
        result = list(collection.aggregate(pipeline))
        return {"grouped_user_data": result}
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
