from flask_sqlalchemy import SQLAlchemy
from src.shared import db
from .city import City 
from .user import User

class Favorites(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)               
    user_id= db.Column(db.Integer , db.ForeignKey('user.id'),nullable=False)
    city_id= db.Column(db.Integer , db.ForeignKey('city.id'),nullable=False)

