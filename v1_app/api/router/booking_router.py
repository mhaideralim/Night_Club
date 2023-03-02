import datetime

from fastapi import APIRouter
from fastapi.params import Depends
from v1_app.api.database.db_connection import get_database
from v1_app.api.model.book_table_model import Booking
import json

router = APIRouter()


@router.post("/book_table")
async def book_table(booking: Booking, user_id: int, db=Depends(get_database)):
    """
    :param booking:
    :param user_id:
    :param db:
    :return:
    """
    try:
        # Check if the user exists in the database
        user = await db.users.find_one({"user_id": user_id})
        if user:
            table = await db.booking.find_one({"table_no": booking.table_no})
            date_str = json.dumps(booking.date.isoformat())  # serialize date field to string
            date = await db.booking.find_one({"date": date_str})
            spec_date = json.dumps(datetime.date.today().isoformat())
            if str(date) < spec_date:
                response = {
                    "code": 0,
                    "message": "Invalid Date",
                    "data": {
                        "validate_errors": [
                            {
                                "message": "You are Entering wrong date!"
                            }
                        ]
                    }
                }
                return response
            elif date and table:
                response = {
                    "code": 0,
                    "message": "Table Already Booked",
                    "data": {
                        "validate_errors": [
                            {
                                "message": "You Can Reserve any other table"
                            },
                            {
                                "message": "You can Book on another Date"
                            }
                        ]
                    }
                }
                return response
            else:
                # Add date field to booking dict as string
                booking_dict = booking.dict()
                booking_dict['date'] = date_str
                await db.booking.insert_one(booking_dict)
                response = {
                    "code": 1,
                    "message": "Table Booked Successfully!",
                    "data": {
                        "user_id": user_id,
                        "booking_data": booking_dict
                    }
                }
                return response
        else:
            response = {
                "code": 0,
                "message": "Invalid User!",
                "data": {
                    "validate_errors": [
                        {
                            "message": "Please Login to Reserve Table "
                        }
                    ]
                }
            }
            return response
    except Exception as e:
        response = {
            "code": 500,
            "message": "Internal Server Error",
            "data": {
                "error": str(e)
            }
        }
        return response
