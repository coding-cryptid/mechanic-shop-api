from flask import jsonify, request
from sqlalchemy import select
from app.blueprints.users import user_bp
from app.models import User, ServiceTicket, db
from app.extensions import limiter
from .schemas import user_schema, users_schema, LoginSchema
from app.utils.util import encode_token, token_required
from werkzeug.security import check_password_hash


login_schema = LoginSchema()

@users_bp.route('/login', methods=[ 'POST' ])
def login():
    """Authenticate user and return JWT token"""
    try:
        credentials = request.json

        errors = login_schema.validate(credentials)
        if errors:
            return jsonify({
                "message": "Invalid payload",
                "errors": errors
            }), 400

        email = credentials["email"]
        password = credentials["password"]

    except TypeError:
        return jsonify({
            "message": "Invalid expecting JSON"
        }), 400

    query = select(User).where(User.email == email)
    user = db.session.execute(query).scalar_one_or_none()

    if user and check_password_hash(user.password, password):
        auth_token = encode_token(user.id)

        return jsonify({
            "status": "success",
            "message": "Successfully Loggd In",
            "auth_token": auth_token
        }), 200

    return jsonify({
        "message": "Invalid email or password"
    }), 401


@users_bp.route('/', methods=['DELETE'])
@token_required
def delete_user(user_id):
    """Delete the authenticated user (requires token)"""
    try:
        query = select(User).where(User.id == user_id)
        user = db.session.execute(query).scalars().first()

        if not user:
            return jsonify({'message': 'User not found'}), 404

        db.session.delete(user)
        db.session.commit()
        return '', 204
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting user', 'error': str(e)}), 500

@users_bp.route('/my-tickets', methods=['GET'])
@token_required
def get_my_tickets(user_id):
    """Get all service tickets for the authenticated user"""
    try:
        query = select(ServiceTicket).where(ServiceTicket.user_id == user_id)
        tickets = db.session.execute(query).scalars().all()

        tickets_data = [
            {
                'id': ticket.id,
                'subject': ticket.subject,
                'description': ticket.description,
                'status': ticket.status,
                'created_at': ticket.created_at.isoformat() if ticket.created_at else None,
                'updated_at': ticket.updated_at.isoformat() if ticket.updated_at else None
            }
            for ticket in tickets
        ]
        
        return jsonify({
            'status': 'success',
            'tickets': tickets_data,
            'count': len(tickets_data)
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Error retrieving tickets', 'error': str(e)}), 500