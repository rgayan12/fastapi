import sys

from fastapi import APIRouter, HTTPException, Depends, Security
from app.controllers.MessageController import handleUsersEvent, getUsers, countEventRegistrations, \
    countRecentRegistrations, getUserDataGroupedByMessage
from app.requests.UserEventRequest import UserEventRequest
from app.requests.MailChimpListCollectionRequest import MailChimpListsRequest, MailChimpList
from app.models.MailChimpListCollectionModel import MailChimpListsModel, MailChimpList
from app.service.MailChimpService import MailChimpService
from fastapi.security.api_key import APIKeyHeader, APIKey
from app.service.RabbitService import RabbitMQService
import pika
from pydantic import BaseModel

router = APIRouter()
mailchimp = MailChimpService()
rabbitMq = RabbitMQService()


@router.post("/event")
async def handleUserEvent(message: UserEventRequest):
    return handleUsersEvent(message)


@router.get('/users')
async def getUserEvents():
    return await getUsers()


@router.get("/event-registrations/count")
async def getEventRegistrations():
    return await countEventRegistrations()


@router.get('/event-registrations/recent')
async def getRecentRegistrations():
    return await countRecentRegistrations()


@router.get('/event-registrations/users')
async def eventDataGrouped():
    return await getUserDataGroupedByMessage()


@router.get('/mailchimp/ping')
async def pingMailChimp():
    response = mailchimp.ping()
    return response


@router.get('/mailchimp/lists/remote')
async def getAllMailChimpLists():
    response = await mailchimp.getAllRemoteLists()
    return response


@router.get('/mailchimp/lists/local')
async def getLocalMailChimpLists():
    try:
        response = await mailchimp.getAllLocalLists()
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/mailchimp/lists/store')
async def storeMailChimpLists(collection: MailChimpListsRequest):
    response = await mailchimp.storeMailChimpLists(collection)
    return response


@router.post('/mailchimp/lists/sync')
async def syncMailChimpLists():
    mailChimpLists = await mailchimp.getAllRemoteLists()
    response = await mailchimp.syncMailChimpList(mailChimpLists)
    return response


@router.post("/rabbitmq/send")
async def send_message(message: UserEventRequest):
    return await rabbitMq.send_message_to_rabbitmq(message.json())
