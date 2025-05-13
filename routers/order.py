from fastapi import APIRouter, HTTPException
from datetime import date
from peewee import DoesNotExist
from typing import List
from models.order import Order
from models.student import Student
from models.book import Book
from schemas.order import OrderCreate, OrderResponse
from schemas.student import StudentResponse
from schemas.book import BookResponse

router = APIRouter(prefix="/orders", tags=["orders"])

BASE_URL = "http://localhost:8000"  



def get_object_or_404(model, obj_id: int, detail: str):
    obj = model.get_or_none(model.id == obj_id)
    if not obj:
        raise HTTPException(status_code=404, detail=detail)
    return obj


def get_order_response(o: Order) -> OrderResponse:
    student_photo_url = f"{BASE_URL}/students/photo/{o.student.photo}" if o.student.photo else None
    book_cover_url = f"{BASE_URL}/books/cover/{o.book.cover_image}" if o.book.cover_image else None

    return OrderResponse(
        id=o.id,
        rented_date=o.rented_date,
        return_date=o.return_date,
        total_days=o.total_days,
        total_rent=o.total_rent,
        rent_per_day=o.rent_per_day,
        student_id=o.student.id,      
        book_id=o.book.id,    
                
        student=StudentResponse(
            id=o.student.id,
            name=o.student.name,
            email=o.student.email,
            photo=student_photo_url
        ),
        
        book=BookResponse(
            id=o.book.id,
            title=o.book.title,
            author=o.book.author,
            cover_image=book_cover_url
        )
    )


# 🔸 Create a new order
@router.post("/", response_model=OrderResponse)
def create_order(order: OrderCreate):
  
    student = get_object_or_404(Student, order.student_id, "Student not found")
    book = get_object_or_404(Book, order.book_id, "Book not found")

    existing_order = Order.get_or_none(
        (Order.book == book) & (Order.return_date.is_null())
    )
    if existing_order:
        raise HTTPException(status_code=400, detail="Book is already rented by another student")

    fixed_rent = 10
    order_db = Order.create(
        student=student,
        book=book,
        rent_per_day=fixed_rent,
        rented_date=date.today(),
        total_days=1,
        total_rent=fixed_rent * 1
    )
    return get_order_response(order_db)



@router.post("/{order_id}/return", response_model=OrderResponse)
def return_book(order_id: int):
  
    try:
        order = Order.get_by_id(order_id)
        if order.return_date is not None:
            raise HTTPException(status_code=400, detail="Book already returned")

        return_date = date.today()
        rented_days = (return_date - order.rented_date).days + 1
        total_rent = rented_days * order.rent_per_day

        order.return_date = return_date
        order.total_days = rented_days
        order.total_rent = total_rent
        order.save()

        return get_order_response(order)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Order not found")



@router.get("/", response_model=List[OrderResponse])
def list_orders():
    orders = Order.select().join(Student).switch(Order).join(Book)
    return [get_order_response(o) for o in orders]



@router.delete("/{order_id}")
def delete_order(order_id: int):
    
    order = Order.get_or_none(Order.id == order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.delete_instance()
    return {"detail": "Order deleted successfully"}


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int):
    order = Order.get_or_none(Order.id == order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return get_order_response(order)



@router.put("/{order_id}", response_model=OrderResponse)
def update_order(order_id: int, updated_data: OrderCreate):
    order = Order.get_or_none(Order.id == order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    student = get_object_or_404(Student, updated_data.student_id, "Student not found")
    book = get_object_or_404(Book, updated_data.book_id, "Book not found")

    
    if book.id != order.book.id:
        existing_order = Order.get_or_none(
            (Order.book == book) & (Order.return_date.is_null())
        )
        if existing_order:
            raise HTTPException(status_code=400, detail="Book is already rented by another student")

    order.student = student
    order.book = book
    order.save()

    return get_order_response(order)

