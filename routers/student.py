import os
import uuid
from pathlib import Path
from fastapi import APIRouter, HTTPException, File, UploadFile, Form, Request
from fastapi.responses import FileResponse
from peewee import DoesNotExist, IntegrityError
from models.student import Student
from models.order import Order
from schemas.student import StudentResponse, StudentUpdate

UPLOAD_FOLDER = "uploads/students"
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

router = APIRouter(prefix="/students", tags=["students"])


def save_student_photo(file: UploadFile) -> str:
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(UPLOAD_FOLDER, filename)
    with open(path, "wb") as f:
        f.write(file.file.read())
    return filename


@router.post("/", response_model=StudentResponse, status_code=201)
async def create_student(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    photo: UploadFile = File(...)
):
    if Student.select().where(Student.email == email).exists():
        raise HTTPException(status_code=409, detail="Email already exists")

    try:
        filename = save_student_photo(photo)
        student = Student.create(name=name, email=email, photo=filename)
        return StudentResponse(
            id=student.id,
            name=student.name,
            email=student.email,
            photo=f"{request.base_url}students/photo/{filename}"
        )
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Database integrity error")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[StudentResponse])
def list_students(request: Request):
    students = Student.select()
    result = []
    for s in students:
        photo_url = f"{request.base_url}students/photo/{s.photo}" if s.photo else None
        result.append(StudentResponse(
            id=s.id,
            name=s.name,
            email=s.email,
            photo=photo_url
        ))
    return result


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, request: Request):
    try:
        s = Student.get_by_id(student_id)
        photo_url = f"{request.base_url}students/photo/{s.photo}" if s.photo else None
        return StudentResponse(
            id=s.id,
            name=s.name,
            email=s.email,
            photo=photo_url
        )
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Student not found")


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    request: Request,
    student_id: int,
    student_update: StudentUpdate,
    photo: UploadFile = File(None)
):
    try:
        student = Student.get_by_id(student_id)

        if student_update.email:
            exists = Student.select().where(
                (Student.email == student_update.email) & (Student.id != student_id)
            ).exists()
            if exists:
                raise HTTPException(status_code=400, detail="Email already in use")

        if student_update.name:
            student.name = student_update.name
        if student_update.email:
            student.email = student_update.email
        if photo:
            student.photo = save_student_photo(photo)

        student.save()
        photo_url = f"{request.base_url}students/photo/{student.photo}" if student.photo else None
        return StudentResponse(
            id=student.id,
            name=student.name,
            email=student.email,
            photo=photo_url
        )

    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Student not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")


@router.delete("/{student_id}")
def delete_student(student_id: int):
    try:
        student = Student.get_by_id(student_id)

        if Order.select().where((Order.student == student) & (Order.return_date.is_null())).exists():
            raise HTTPException(status_code=400, detail="Cannot delete student with active order")

        if student.photo:
            path = os.path.join(UPLOAD_FOLDER, student.photo)
            if os.path.exists(path):
                os.remove(path)

        student.delete_instance()
        return {"message": "Student deleted successfully"}

    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Student not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting student: {str(e)}")


@router.get("/photo/{filename}")
def get_student_photo(filename: str):
    path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Photo not found")
    return FileResponse(path)
