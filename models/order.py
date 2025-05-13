from peewee import Model, IntegerField, ForeignKeyField, DateField
from database.database import db
from models.student import Student
from models.book import Book

class BaseDBModel(Model):
    class Meta:
        database = db

class Order(BaseDBModel):
    id = IntegerField(primary_key=True)
    student = ForeignKeyField(Student, backref='orders')
    book = ForeignKeyField(Book, backref='orders')
    rent_per_day = IntegerField(default=10)
    rented_date = DateField()
    return_date = DateField(null=True)
    total_days = IntegerField(default=0)
    total_rent = IntegerField(default=0)