from functools import wraps
import os
from datetime import datetime, timedelta
from flask import request, jsonify
from jose import jwt, exceptions as jose_exceptions


SECRET_KEY = os.environ.get('SECRET_KEY') or "super secret secrets"
ALGORITHM = "HS256"


def encode_token(user_id):
    """Create JWT token with user_id as 'sub' claim"""
    try:
        payload = {
            'sub': str(user_id),   # <-- convert to string
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }

        return jwt.encode(
            payload,
            SECRET_KEY,
            algorithm=ALGORITHM
        )

    except Exception as e:
        print("TOKEN ENCODE ERROR:", e)
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
                return jsonify({
                    'message': 'Invalid authorization header format'
                }), 401

        if not token:
            return jsonify({
                'message': 'Token is missing!'
            }), 401

        try:
            data = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=[ALGORITHM]
            )

            # sub comes back as a string, so convert it to an int
            user_id = int(data['sub'])

        except jose_exceptions.ExpiredSignatureError:
            return jsonify({
                'message': 'Token has expired!'
            }), 401

        except jose_exceptions.JWTError as e:
            print("JWT ERROR:", e)
            return jsonify({
                'message': 'Invalid token!'
            }), 401

        return f(user_id, *args, **kwargs)

    return decorated