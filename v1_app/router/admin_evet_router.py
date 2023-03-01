from fastapi import APIRouter, HTTPException
from fastapi.params import Depends

from v1_app.database.db_connection import get_database
from v1_app.model.event_model import EventData

router = APIRouter()


@router.post("/save-event-data")
async def save_event_data(event: EventData, admin_id: int, db=Depends(get_database)):
    try:
        data = await db.users.find_one({"admin_id": admin_id})
        if data:
            await db.eventdata.insert_one(event)
            return HTTPException(status_code=200, detail="Data Saved Successfully!")
        else:
            return HTTPException(status_code=400, detail="Admin Not Found!")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

