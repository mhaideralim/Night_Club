from fastapi import APIRouter, HTTPException
from fastapi.params import Depends

from v1_app.database.db_connection import get_database
from v1_app.model.event_model import EventData

router = APIRouter()


@router.get("/show-event")
async def show_event_data(event: EventData, user_id: str, db=Depends(get_database)):
    try:
        data = await db.eventdata.find_one({"user_id": user_id})
        if data:
            return HTTPException(status_code=200, detail={"event": event})
        else:
            return HTTPException(status_code=404, detail="Invalid User")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/book-event-ticket")
async def book_event_ticket(members_joining: list, user_id: str, db=Depends(get_database)):
    try:
        data = await db.eventdata.find_one({"user_id": user_id})
        if data:
            await db.eventdata.append({"members_joining": members_joining})
            return HTTPException(status_code=200, detail="Member Added Successfully!")
        else:
            return HTTPException(status_code=404, detail="ID Not Found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
