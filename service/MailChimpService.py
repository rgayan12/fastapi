import sys

from fastapi import FastAPI
from dotenv import load_dotenv
import os
from mailchimp_marketing import Client
from mailchimp_marketing.api_client import ApiClientError
from typing import List
from app.config.database import mongodb
from pymongo.errors import PyMongoError
from fastapi import HTTPException
from app.requests.MailChimpListCollectionRequest import MailChimpListsRequest
from app.requests.UserEventRequest import UserEventRequest
import requests


class MailChimpService:
    defaultAudienceId = "5ba533e249"

    def __init__(self):
        load_dotenv()
        self.mailchimp = Client()
        self.mailchimp.set_config({
            "api_key": os.getenv("MAILCHIMP_AUTH_KEY", ""),
            "server": os.getenv("MAILCHIMP_SERVER_PREFIX")
        })

    def ping(self):
        response = self.mailchimp.ping.get()
        return response

    def syncContact(self, mailChimpContact: UserEventRequest):

        memberInfo = {
            "email_address": mailChimpContact.userData.email,
            "status": mailChimpContact.userData.marketing_opt_in,
            "tags": [
                mailChimpContact.identifier,
            ],
            'merge_fields': {
                "FNAME": mailChimpContact.userData.first_name,
                "LNAME": mailChimpContact.userData.last_name,
                "PHONE": mailChimpContact.userData.phone,
                "IS_AN_ADULT": mailChimpContact.userData.over_18,
            }
        }

        url = os.getenv('MAILCHIMP_BASE_URL') + "/lists/5ba533e249/members"
        auth = ('anystring', os.getenv('MAILCHIMP_AUTH_KEY'))  # MailChimp API key auth

        try:
            response = requests.post(url, json=memberInfo, auth=auth)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as error:
            error_message = f"MailChimp API error: {error.response.text}"
            print(f"An exception occurred: {error_message}")
            raise HTTPException(status_code=500, detail=error_message)
        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            print(f"An unexpected exception occurred: {error_message}")
            raise HTTPException(status_code=500, detail=error_message)

    async def getAllRemoteLists(self):
        response = self.mailchimp.lists.get_all_lists(
            fields=[
                "lists.id",
                "lists.web_id",
                "lists.name",
                "lists.list_rating",
                "lists.stats"
            ],
            count=1000
        )
        return response

    async def getAllLocalLists(self):
        try:
            collections = mongodb.get_collection("mailchimp_lists")
            results = collections.find()
            mailchimpList = []
            for item in results:
                item['_id'] = str(item['_id'])  # Convert ObjectId to string
                mailchimpList.append(item)
            return mailchimpList
        except PyMongoError as e:
            raise HTTPException(status_code=500, detail=f"Database retrieval error")

    async def storeMailChimpLists(self, mailChimpList: MailChimpListsRequest):
        try:
            collection = mongodb.get_collection("mailchimp_lists")
            # Delete all existing documents
            collection.delete_many({})
            mailChimpLists_dicts = [list_item.dict() for list_item in mailChimpList.lists]
            result = collection.insert_many(mailChimpLists_dicts)
            return {"inserted_ids": [str(id) for id in result.inserted_ids]}
        except PyMongoError as e:
            raise HTTPException(status_code=500, detail=f"Error Inserting Collection: {e}")

    async def syncMailChimpList(self, chimpListsCollection: List[dict]):
        try:
            collection = mongodb.get_collection("mailchimp_lists")
            # Delete all existing documents
            collection.delete_many({})
            result = collection.insert_many(chimpListsCollection['lists'])
            return {"inserted_ids": [str(id) for id in result.inserted_ids]}
        except PyMongoError as e:
            raise HTTPException(status_code=500, detail=f"Error Inserting Collection: {e}")
