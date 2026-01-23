from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    id:int
    name:str
    email:EmailStr

class UserResponse(BaseModel):
    id:int
    name:str
    email:EmailStr



