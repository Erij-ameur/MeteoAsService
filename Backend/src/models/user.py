from flask_sqlalchemy import SQLAlchemy

from src.shared import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(500))

    favorites = db.relationship('Favorites', backref='user', lazy=True)

    def __repr__(self):
        return "<User '{}'>".format(self.email)
   