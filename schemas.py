from pydantic import BaseModel, field_validator
import re
from typing import Any, List, Optional

class Interest(BaseModel):
    id: int
    name: str
class UserBase(BaseModel):
    name: str
    age: int
    gender: str
    email: str
    city: str
    interests: Optional[List[Interest]] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$",value):
            raise ValueError('Email is not in valid format')
        return value

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

