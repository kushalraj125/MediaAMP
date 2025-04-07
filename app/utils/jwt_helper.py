import jwt
import datetime
from flask import request, jsonify
from functools import wraps
from config import JWT_SECRET, JWT_EXPIRY_HOURS

def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.now() + datetime.timedelta(hours=JWT_EXPIRY_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def decode_token(token):
    return jwt.decode(token, JWT_SECRET, algorithms=['HS256'])

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            bearer = request.headers['Authorization']
            token = bearer.split(" ")[1] if " " in bearer else bearer
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        try:
            data = decode_token(token)
            request.user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated
