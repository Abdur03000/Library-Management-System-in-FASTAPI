from peewee import Model, IntegerField, CharField
from database.database import db

class BaseDBModel(Model):
    class Meta:
        database = db

class Book(BaseDBModel):
    id = IntegerField(primary_key=True)
    title = CharField(null=False)
    author = CharField(null=False)
    cover_image = CharField(null=True) 
