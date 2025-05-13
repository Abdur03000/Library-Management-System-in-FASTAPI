import os
import uuid
from pathlib import Path
from fastapi import APIRouter, HTTPException, File, UploadFile, Form, Request, status
from fastapi.responses import FileResponse
from peewee import DoesNotExist, IntegrityError
from models.book import Book
from models.order import Order
from schemas.book import BookResponse, BookUpdate

UPLOAD_FOLDER = "uploads/books"
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

router = APIRouter(prefix="/books", tags=["books"])


def save_cover_image(file: UploadFile) -> str:
    allowed_exts = [".jpg", ".jpeg", ".png"]
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(UPLOAD_FOLDER, filename)

    with open(path, "wb") as f:
        f.write(file.file.read())

    return filename  


@router.post("/", response_model=BookResponse, status_code=201)
async def create_book(
    request: Request,
    title: str = Form(...),
    author: str = Form(...),
    cover_image: UploadFile = File(...)
):
    if Book.select().where(Book.title == title).exists():
        raise HTTPException(status_code=409, detail="Book already exists")

    try:
        filename = save_cover_image(cover_image)
        book = Book.create(title=title, author=author, cover_image=filename)

        return BookResponse(
            id=book.id,
            title=book.title,
            author=book.author,
            cover_image=f"{request.base_url}books/cover/{filename}"
        )

    except IntegrityError:
        raise HTTPException(status_code=400, detail="Database integrity error")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[BookResponse])
def list_books(request: Request):
    books = Book.select()
    result = []

    for b in books:
        cover_url = f"{request.base_url}books/cover/{b.cover_image}" if b.cover_image else None
        result.append(BookResponse(
            id=b.id,
            title=b.title,
            author=b.author,
            cover_image=cover_url
        ))

    return result


@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, request: Request):
    try:
        book = Book.get_by_id(book_id)
        cover_url = f"{request.base_url}books/cover/{book.cover_image}" if book.cover_image else None
        return BookResponse(
            id=book.id,
            title=book.title,
            author=book.author,
            cover_image=cover_url
        )
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Book not found")


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    request: Request,
    book_id: int,
    book_update: BookUpdate,
    cover_image: UploadFile = File(None)
):
    try:
        book = Book.get_by_id(book_id)

        if book_update.title:
            exists = Book.select().where(
                (Book.title == book_update.title) & (Book.id != book_id)
            ).exists()
            if exists:
                raise HTTPException(status_code=400, detail="Title already in use")

        if book_update.title:
            book.title = book_update.title
        if book_update.author:
            book.author = book_update.author
        if cover_image:
            
            if book.cover_image:
                old_path = os.path.join(UPLOAD_FOLDER, book.cover_image)
                if os.path.exists(old_path):
                    os.remove(old_path)

            
            book.cover_image = save_cover_image(cover_image)

        book.save()
        cover_url = f"{request.base_url}books/cover/{book.cover_image}" if book.cover_image else None
        return BookResponse(
            id=book.id,
            title=book.title,
            author=book.author,
            cover_image=cover_url
        )

    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Book not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")


@router.delete("/{book_id}", status_code=status.HTTP_200_OK)
def delete_book(book_id: int):
    try:
        book = Book.get_by_id(book_id)

        if Order.select().where((Order.book == book) & (Order.return_date.is_null())).exists():
            raise HTTPException(status_code=400, detail="Cannot delete book that is currently rented")

        
        if book.cover_image:
            path = os.path.join(UPLOAD_FOLDER, book.cover_image)
            if os.path.exists(path):
                os.remove(path)

        book.delete_instance()
        return {"message": "Book deleted successfully"}

    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Book not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting book: {str(e)}")


@router.get("/cover/{filename}")
def get_cover_image(filename: str):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path)
