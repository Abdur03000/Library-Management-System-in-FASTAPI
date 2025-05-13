from pydantic import BaseModel, EmailStr
from typing import Optional

class StudentCreate(BaseModel):
    name: str
    email: EmailStr
    photo: Optional[str] = None

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    photo: Optional[str] = None

class StudentResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    photo: Optional[str]

    class Config:
        from_attributes = True

        
        