from enum import Enum
from pydantic import BaseModel, EmailStr
from typing import Optional


class MarketingOptIn(str, Enum):
    subscribed = 'subscribed'
    unsubscribed = 'unsubscribed'


class UserData(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    over_18: Optional[str] = None
    marketing_opt_in: MarketingOptIn


class UserEventRequest(BaseModel):
    message: str
    identifier: str
    userData: UserData
