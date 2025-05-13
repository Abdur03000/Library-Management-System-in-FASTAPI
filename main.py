from fastapi import FastAPI
from database.database import init_db
from routers import student, book, order


app = FastAPI()

# Initialize database
init_db()

# Include routers
app.include_router(student.router)
app.include_router(book.router)
app.include_router(order.router)

@app.get("/")
def read_root():
    return {"message": "Library Management System"}