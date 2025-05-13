from peewee import SqliteDatabase

db = SqliteDatabase('library.db')

def init_db():
    db.connect()
    # Import models here to avoid circular imports
    from models.student import Student
    from models.book import Book
    from models.order import Order
    db.create_tables([Student, Book, Order], safe=True)
    db.close()