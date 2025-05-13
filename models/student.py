from peewee import Model, IntegerField, CharField
from database.database import db

class BaseDBModel(Model):
    class Meta:
        database = db

class Student(BaseDBModel):
    id = IntegerField(primary_key=True)
    name = CharField(null=False)
    email = CharField(null=False, unique=True)
    photo = CharField(null=True) 

   