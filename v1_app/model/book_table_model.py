import datetime
from pydantic import BaseModel, constr


class Booking(BaseModel):

    booking_id: int
    date: datetime.date
    time: datetime.time
    table_no: str
    name: str
    email: constr(regex=r"[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+")
    phone_no: int
    instagram_id: str
