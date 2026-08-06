from functools import wraps
from datetime import datetime, timedelta
from flask import request, jsonify
from jose import jwt, exceptions as jose_exceptions


SECRET_KEY = "a super secret, secret key"
ALGORITHM = "HS256"

def encode_token(user_id):
    """Create JWT token with user_id as 'sub' claim"""
    try:
        payload = {
            'sub': user_id,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Invalid authorization header format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = data['sub'] 

        except jose_exceptions.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jose_exceptions.JWTError:
            return jsonify({'message': 'Invalid token!'}), 401

        return f(user_id, *args, **kwargs)

    return decorated