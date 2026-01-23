from pydantic import BaseModel
from fastapi_users import schemas
import uuid

class PosteCreate(BaseModel):
    title: str
    content: str

class PosteResponse(BaseModel):
    title: str
    content: str

class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass

class UserUpdate(schemas.BaseUserUpdate):
    pass