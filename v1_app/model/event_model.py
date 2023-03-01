import datetime
from typing import List

from pydantic import BaseModel


class EventData(BaseModel):
    event_id: int
    event_name: str
    about: str
    address: str
    ticket_price: float
    guest_list: List[str] = []
    members_joining: List[str] = []




