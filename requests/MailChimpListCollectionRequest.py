from pydantic import BaseModel, Field
from typing import List, Optional


class Stats(BaseModel):
    member_count: Optional[int]
    unsubscribe_count: Optional[int]
    cleaned_count: Optional[int]
    member_count_since_send: Optional[int]
    unsubscribe_count_since_send: Optional[int]
    cleaned_count_since_send: Optional[int]
    campaign_count: Optional[int]
    campaign_last_sent: Optional[str]
    merge_field_count: Optional[int]
    avg_sub_rate: Optional[float]
    avg_unsub_rate: Optional[float]
    target_sub_rate: Optional[float]
    open_rate: Optional[float]
    click_rate: Optional[float]
    last_sub_date: Optional[str]
    last_unsub_date: Optional[str]


class MailChimpList(BaseModel):
    id: str
    web_id: int
    name: str
    list_rating: Optional[int]
    stats: Optional[Stats]


class MailChimpListsRequest(BaseModel):
    lists: List[MailChimpList]
