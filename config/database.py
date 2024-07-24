import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class MongoDB:
    def __init__(self, uri: str, database: str):
        self.client = MongoClient(uri)
        self.database = self.client[database]

    def get_collection(self, collection_name: str):
        return self.database[collection_name]


mongodb = MongoDB(
    uri=os.getenv("MONGODB_URI"),
    database=os.getenv("MONGODB_DATABASE")
)
