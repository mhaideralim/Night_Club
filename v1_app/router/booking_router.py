from fastapi import APIRouter, HTTPException
from fastapi.params import Depends

from v1_app.database.db_connection import get_database
from v1_app.model.book_table_model import Booking

router = APIRouter()


@router.post("/book_table")
def book_table(booking: Booking, user_id: int, db=Depends(get_database)):
    try:
        # Check if the user exists in the database
        user = db.users.find_one({"user_id": user_id})
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if the requested table is available on the specified date and time
        else:
            table = db.booking.find_one({"date": booking.date, "table_no": booking.table_no})
            if table:
                raise HTTPException(status_code=409, detail="Table is already booked")
            # Book the table for the user
            db.booking.insert_one(booking.dict())
        # Return the booking confirmation to the user
        return {"message": "Table booked successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
