from pydantic import BaseModel
from datetime import date
from typing import Optional
from schemas.student import StudentResponse
from schemas.book import BookResponse

class OrderCreate(BaseModel):
    student_id: int
    book_id: int

class OrderResponse(BaseModel):
    id: int
    rented_date: date
    return_date: Optional[date]
    total_days: int
    total_rent: int
    rent_per_day: int
    student_id: int                 
    book_id: int                 
    student: StudentResponse
    book: BookResponse

    class Config:
        from_attributes = True


    
class OrderUpdate(BaseModel):
    student_id: Optional[int] = None
    book_id: Optional[int] = None
    return_date: Optional[date] = None


    student: StudentResponse
    book: BookResponse

    class Config:
        from_attributes = True
