from functools import wraps
from flask import request, jsonify
from jose import jwt, exceptions as jose_exceptions


SECRET_KEY = "a super secret, secret key"

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = data['sub'] 

        except jose_exceptions.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jose_exceptions.JWTError:
            return jsonify({'message': 'Invalid token!'}), 401

        return f(user_id, *args, **kwargs)

    return decorated