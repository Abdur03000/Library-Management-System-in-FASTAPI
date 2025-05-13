from pydantic import BaseModel
from typing import Optional

class BookCreate(BaseModel):
    title: str
    author: str
    cover_image: Optional[str] = None  

class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    cover_image: Optional[str] = None

    class Config:
        from_attributes = True

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    cover_image: Optional[str] = None

    class Config:
        from_attributes = True
