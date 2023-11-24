from datetime import timedelta
from flask import Flask 
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os

from .shared import db 

from .models.city import City
from .models.user import User 
from .models.favorites import  Favorites

from src.controllers.userC import user
from src.controllers.cityC import city

def create_app():
    app=Flask(__name__)

    app.config.from_mapping(
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_DATABASE_URI='postgresql://postgres:admin@localhost/weatherApp',
        JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY'),
        JWT_EXPIRATION_DELTA = timedelta(hours=24)
    ) 
   
    CORS(app)
    db.init_app(app)
    JWTManager(app)

    @app.route('/')
    def hello():
        return 'hey!'


    with app.app_context():
        db.create_all()

    app.register_blueprint(user)
    app.register_blueprint(city)

    return app

