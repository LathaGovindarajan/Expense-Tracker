# tracker/models.py
from mongoengine import Document, StringField, FloatField, DateTimeField, ReferenceField
import datetime

class Category(Document):
    category      = StringField(required=True, unique=True)   # name
    description   = StringField()
    goal          = FloatField(default=0.0)                   # monthly goal
    date_created  = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'category',
        'ordering': ['category']   # default ordering by category name
    }

class User(Document):
    username        = StringField(required=True, unique=True)
    password        = StringField(required=True)
    salary          = FloatField(default=0.0)
    spending_goal   = FloatField(default=0.0)
    alert_threshold = FloatField(default=0.0)

    meta = {
        'collection': 'user',
        'ordering': ['username']   # default ordering by username
    }

class Expense(Document):
    user        = ReferenceField(User, required=True)
    category    = ReferenceField(Category, required=True)
    amount      = FloatField(required=True)
    description = StringField()
    date        = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'expenses',
        'ordering': ['-date']    # default ordering: newest first
    }
