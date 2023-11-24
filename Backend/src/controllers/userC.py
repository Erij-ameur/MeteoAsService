from flask import Blueprint,request, jsonify
from ..models.user import db,User
from ..models.favorites import db,Favorites
from ..constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT, HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT
import validators
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity

user = Blueprint("user",__name__,url_prefix="/api/user")

@user.post('/register')
def register():
    email = request.json['email']
    password = request.json['password']

    if not validators.email(email):
        return jsonify({'error': "Email is not valid"}), HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'error': "Email is taken"}), HTTP_409_CONFLICT

    if len(password) < 6:
        return jsonify({'error': "Password is too short"}), HTTP_400_BAD_REQUEST

    pwd_hash = generate_password_hash(password)

    new_user = User(
            email=email,
            password=pwd_hash
        )

    db.session.add(new_user)
    db.session.commit()
    return jsonify({
        'message': "User created",
        'user': {
            "email": email
        }

    }), HTTP_201_CREATED





@user.post('/login')
def login():
    email = request.json.get('email', '')
    password = request.json.get('password', '')

    user = User.query.filter_by(email=email).first()
    if user:
        is_pass_correct = check_password_hash(user.password, password)
        if is_pass_correct:
            access = create_access_token(identity=user.id)

            return jsonify({
                'user': {
                    'access': access,
                    'email': user.email
                }

            }), HTTP_200_OK

    return jsonify({'error': 'Wrong credentials'}), HTTP_401_UNAUTHORIZED




@user.get('/me')
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    
    return jsonify({
        'email': user.email
    }), HTTP_200_OK



@user.get('/all')
def get_all_users():
    users = User.query
    data = []
    for u in users :
        data.append ({
            'id':u.id,
            'email':u.email
        })

    return jsonify({'data': data}), HTTP_200_OK



@user.route('/fav' , methods=['POST','GET'] )
@jwt_required()
def handle_favorite():

    if request.method == 'POST':
        city_id=request.get_json().get('city_id','')
        if Favorites.query.filter_by(city_id=city_id).first():
            return jsonify({
                'error':'already exixts'
            }),HTTP_409_CONFLICT
        
        fav=Favorites(city_id=city_id,user_id=get_jwt_identity())
        db.session.add(fav)
        db.session.commit()

        return jsonify({
                    'favorite': {
                        'id': fav.id,
                        'user_id': fav.user_id,
                        'city_id': fav.city_id
                    }
                }), HTTP_200_OK
    
    else:
        favorites = Favorites.query.filter_by(user_id=get_jwt_identity())
        data =[]
        for f in favorites:
            data.append({
                'id':f.id,
                'user_id': f.user_id,
                'city_id': f.city_id
            })
        return jsonify({'favorites': data}), HTTP_200_OK



@user.delete("/fav/<int:id>")
@jwt_required()
def delete_favorite(id):
    favorite = Favorites.query.filter_by(user_id=get_jwt_identity(), id=id).first()

    if not favorite:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({}), HTTP_204_NO_CONTENT