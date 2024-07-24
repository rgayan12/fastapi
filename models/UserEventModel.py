from app.config.database import mongodb
from pymongo.errors import PyMongoError
from fastapi import HTTPException
from pymongo.errors import PyMongoError
from app.service.EncryptionService import EncryptionService  # Make sure to import your encryption service
from datetime import datetime


class UserEventModel:

    def storeUserEvent(self, item):
        try:
            collection = mongodb.get_collection("user_events")
            document = item.dict()
            document['timestamp'] = datetime.utcnow()  # Add the timestamp
            result = collection.insert_one(document)

        except PyMongoError as e:
            raise HTTPException(status_code=500, detail=f"Database insertion error: {e}")

        return {"inserted_id": str(result.inserted_id)}

