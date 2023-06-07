from pydantic import BaseModel
from typing import List


class UserBase(BaseModel):
    email: str
    pass


class UserCreate(UserBase):
    password: str
    fullName: str


class User(UserBase):
    id: int
    is_active: bool
    class Config:
        orm_mode = True

class ProfileBase(BaseModel):
    email: str
    user_id:int
    pass

class ProfileCreate(ProfileBase):
    {}


class Profile(ProfileBase):
    fullName:str
    avatar:str
    class Config:
        orm_mode = True

