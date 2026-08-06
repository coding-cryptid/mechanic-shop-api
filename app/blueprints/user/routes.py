from flask import jsonify, request
from sqlalchemy import select
from app.blueprints.user import user_bp
from app.models import User, db
from app.extensions import limiter
from .schemas import user_schema, users_schema
from app.utils.util import encode_token, token_required

@user_bp.route("/login", methods=['POST'])
def login():
    try:
        credentials = request.json
        username = credentials['email']
        password = credentials['password']
    except KeyError:
        return jsonify({'messages': 'Invalid payload, expecting username and password'}), 400
    
    query =select(User).where(User.email == email) 
    user = db.session.execute(query).scalar_one_or_none()

    if user and user.password == password: 
        auth_token = encode_token(user.id, user.role.role_name)

        response = {
            "status": "success",
            "message": "Successfully Logged In",
            "auth_token": auth_token
        }
        return jsonify(response), 200
    else:
        return jsonify({'messages': "Invalid email or password"}), 401

@user_bp.route('/', methods=['DELETE'])
@token_required
def delete_user(user_id):
    query = select(User).where(User.id == user_id)
    user = db.session.execute(query).scalars().first()

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"succesfully deleted user {user_id}"})