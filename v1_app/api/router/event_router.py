from fastapi import APIRouter
from fastapi.params import Depends

from v1_app.api.database.db_connection import get_database
from v1_app.api.model.event_model import EventData

router = APIRouter()


@router.get("/show-event")
async def show_event_data(event: EventData, user_id: str, db=Depends(get_database)):
    try:
        data = await db.eventdata.find_one({"user_id": user_id})
        if data:
            response = {
                "code": 1,
                "message": "Success",
                "data": {
                    "event": event
                }
            }
            return response
        else:
            response = {
                "code": 0,
                "message": "Invalid User",
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


@router.post("/book-event-ticket")
async def book_event_ticket(members_joining: list, user_id: str, db=Depends(get_database)):
    try:
        data = await db.eventdata.find_one({"user_id": user_id})
        if data:
            await db.eventdata.append({"members_joining": members_joining})
            response = {
                "code": 1,
                "message": "Success",
                "data": {
                    "members_joining": members_joining
                }
            }
            return response
        else:
            response = {
                "code": 0,
                "message": "Invalid User",
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
