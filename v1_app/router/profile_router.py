from fastapi import APIRouter, HTTPException
from fastapi.params import Depends

from v1_app.database.db_connection import get_database
from v1_app.model.user_profile_model import UserProfile

router = APIRouter()


@router.post("/set-profile-data")
async def set_profile_data(user: UserProfile, user_id: int, db=Depends(get_database)):
    try:
        data = await db.users.find_one({"user_id": user_id})
        print(data)
        if data:
            await db.profile.insert_one(user.dict())
            return HTTPException(status_code=200, detail="Data Stored Successfully!")
        else:
            return HTTPException(status_code=404, detail="No Such User exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
