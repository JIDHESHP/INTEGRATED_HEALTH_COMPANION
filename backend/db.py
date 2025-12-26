from flask import g
from pymongo import MongoClient

def get_db():
    if 'db' not in g:
        client = MongoClient('mongodb://localhost:27017/')
        g.db = client['smart_wellness_db']
    return g.db

def init_db(app):
    with app.app_context():
        # Optional: Index creation or initial setup can go here
        pass
