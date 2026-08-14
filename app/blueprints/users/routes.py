from flask import jsonify, request
from sqlalchemy import select
from app.blueprints.users import users_bp
from app.models import Service_Tickets, Users, Customer, db
from app.extensions import limiter
from .schemas import user_schema, users_schema, LoginSchema, UserSchema
from app.utils.util import encode_token, token_required
from werkzeug.security import check_password_hash


login_schema = LoginSchema()
user_schema = UserSchema()

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

    query = select(Users).where(Users.email == email)
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
        query = select(Users).where(Users.id == user_id)
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
        # Find the logged-in user
        user = db.session.execute(
            select(Users).where(Users.id == user_id)
        ).scalar_one_or_none()

        if not user:
            return jsonify({
                'message': 'User not found'
            }), 404

        # TEMPORARY DEBUGGING
        print("JWT user_id:", user_id)
        print("Logged in user:", user.id, user.email)

        customers = db.session.execute(
            select(Customer)
        ).scalars().all()

        for c in customers:
            print("Customer:", c.id, c.email)

        # Find the customer account with the same email
        customer = db.session.execute(
            select(Customer).where(Customer.email == user.email)
        ).scalar_one_or_none()

        if not customer:
            return jsonify({
                'message': 'Customer account not found'
            }), 404

        # Get tickets belonging to that customer
        tickets = db.session.execute(
            select(Service_Tickets).where(
                Service_Tickets.customer_id == customer.id
            )
        ).scalars().all()

        tickets_data = [
            {
                'id': ticket.id,
                'customer_id': ticket.customer_id,
                'vin': ticket.vin,
                'service_date': (
                    ticket.service_date.isoformat()
                    if ticket.service_date
                    else None
                ),
                'service_description': ticket.service_description
            }
            for ticket in tickets
        ]

        return jsonify({
            'status': 'success',
            'tickets': tickets_data,
            'count': len(tickets_data)
        }), 200

    except Exception as e:
        return jsonify({
            'message': 'Error retrieving tickets',
            'error': str(e)
        }), 500