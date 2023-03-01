from pydantic import BaseModel, constr


class UserProfile(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    email: constr(regex=r"[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+")
