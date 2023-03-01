from fastapi import APIRouter
from fastapi.params import Depends
from v1_app.api.database.db_connection import get_database
from v1_app.api.model.book_table_model import Booking

router = APIRouter()


@router.post("/book_table")
async def book_table(booking: Booking, user_id: int, db=Depends(get_database)):
    try:
        # Check if the user exists in the database
        user = await db.users.find_one({"user_id": user_id})
        if user:
            table = await db.booking.find_one({"table_no": booking.table_no})
            print(table)
            date = await db.booking.find_one({"date": booking.date})  # convert date to string
            print(date)
            if date == booking.date and table == booking.table_no:
                response = {
                    "code": 1,
                    "message": "Table Already Booked",
                    "data": {}
                }
                return response
            else:
                # Add date field to booking dict as string
                await db.booking.insert_one(booking.dict())
                response = {
                    "code": 1,
                    "message": "Table Booked Successfully!",
                    "data": {}
                }
                return response
        else:
            response = {
                "code": 0,
                "message": "Invalid User!",
                "data": {}
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
