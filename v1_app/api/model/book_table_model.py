import datetimejson
import datetime
from pydantic import BaseModel, constr


class Booking(BaseModel):
    booking_id: int | None = None
    date: datetime.date
    phone_no: constr(regex=r"^[0-9]{11}$")
    table_no: str
    name: str
    email: constr(regex=r"[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+")
    instagram_id: str



