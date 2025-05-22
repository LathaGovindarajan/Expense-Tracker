# tracker/models.py
from mongoengine import Document, StringField, FloatField, DateTimeField, ReferenceField
import datetime

class Category(Document):
    category     = StringField(required=True, unique=True)
    description  = StringField(required=True)
    goal         = FloatField(default=0.0)               # ← your per-category goal
    date_created = DateTimeField(default=datetime.datetime.utcnow)
    amount       = FloatField(default=0.0)
    date         = DateTimeField(default=datetime.datetime.utcnow)

class User(Document):
    username        = StringField(required=True, unique=True)
    password        = StringField(required=True)
    salary          = FloatField(default=0.0)
    spending_goal   = FloatField(default=0.0)
    alert_threshold = FloatField(default=0.0)

class Expense(Document):
    user        = ReferenceField(User, required=True)
    category    = ReferenceField(Category, required=True)
    amount      = FloatField(required=True)
    description = StringField()
    date        = DateTimeField(default=datetime.datetime.utcnow)
