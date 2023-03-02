from fastapi import APIRouter
from fastapi.params import Depends

from v1_app.api.database.db_connection import get_database
from v1_app.api.model.user_profile_model import UserProfile

router = APIRouter()


@router.post("/set-profile-data")
async def set_profile_data(user: UserProfile, user_id: int, db=Depends(get_database)):
    """
    :param user:
    :param user_id:
    :param db:
    :return:
    """
    try:
        data = await db.users.find_one({"user_id": user_id})
        print(data)
        if data:
            await db.profile.insert_one(user.dict())
            response = {
                "code": 1,
                "message": "Data Stored Successfully",
                "data": {
                    "user_id": user_id,
                    "user_profile": user.dict()
                }
            }
            return response
        else:
            response = {
                "code": 0,
                "message": "No Such user Exists!",
                "data": {
                    "validate_error": [
                        {
                            "message": "Please Login to Build Profile"
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
