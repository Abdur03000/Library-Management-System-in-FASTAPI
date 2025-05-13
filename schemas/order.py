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

    student: StudentResponse
    book: BookResponse

    class Config:
        from_attributes = True
