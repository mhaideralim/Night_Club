from fastapi import APIRouter
from fastapi.params import Depends

from v1_app.api.database.db_connection import get_database
from v1_app.api.model.event_model import EventData

router = APIRouter()


@router.post("/save-event-data")
async def save_event_data(event: EventData, admin_id: int, db=Depends(get_database)):
    """
    :param event:
    :param admin_id:
    :param db:
    :return:
    """
    try:
        data = await db.users.find_one({"admin_id": admin_id})
        if data:
            await db.eventdata.insert_one(event)
            response = {
                "code": 1,
                "message": "Data Saved Successfully!",
                "data": {"event": event}
            }
            return response
        else:
            response = {
                "code": 0,
                "message": "Admin Not Found!",
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
