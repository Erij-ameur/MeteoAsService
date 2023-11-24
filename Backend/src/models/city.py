from flask_sqlalchemy import SQLAlchemy

from src.shared import db


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)

    def __repr__(self):
        return "<City '{}'>".format(City.name)
    
    def __init__ (self, name):
        self.name = name 