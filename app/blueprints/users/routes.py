from flask import request, jsonify
from sqlalchemy import select
from werkzeug.security import check_password_hash
from app.models import Users, Customer, Service_Tickets, db
from app.utils.util import encode_token, token_required
from . import users_bp
from .schemas import user_schema, service_tickets_schema
from marshmallow import ValidationError


@users_bp.route('/login', methods=['POST'])
def login():
    """
    Login endpoint - validates credentials and returns JWT token
    
    Expected JSON:
    {
        "email": "user@example.com",
        "password": "password123"
    }
    """
    try:
        credentials = request.get_json()

        # ✅ FIX: Check for empty JSON before processing
        if not credentials:
            return jsonify({
                "message": "Invalid expecting JSON"
            }), 400

        # Validate required fields
        if not credentials.get("email") or not credentials.get("password"):
            return jsonify({
                "message": "Email and password are required"
            }), 400

        email = credentials["email"].strip()  # Strip whitespace from email
        password = credentials["password"]

        user = db.session.execute(
            select(Users).where(Users.email == email)
        ).scalar_one_or_none()

        if not user:
            return jsonify({"message": "Invalid email or password"}), 401

        if not check_password_hash(user.password, password):
            return jsonify({"message": "Invalid email or password"}), 401

        # Get customer associated with this user (if any)
        customer = db.session.execute(
            select(Customer).where(Customer.email == email)
        ).scalar_one_or_none()

        token = encode_token(user.id)

        return jsonify({
            "status": "success",
            "message": "Login successful",
            "auth_token": token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "customer_id": customer.id if customer else None
            }
        }), 200

    except ValueError as e:
        return jsonify({
            "message": "Invalid payload",
            "error": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "message": "Error logging in",
            "error": str(e)
        }), 500


@users_bp.route('/my-tickets', methods=['GET'])
@token_required
def get_my_tickets(user_id):
    """
    Get all service tickets for the authenticated user
    Requires valid JWT token in Authorization header
    
    Returns tickets for the customer account associated with the user's email
    """
    try:
        # Get user
        user = db.session.execute(
            select(Users).where(Users.id == user_id)
        ).scalar_one_or_none()
        
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        # Get customer associated with this user's email
        customer = db.session.execute(
            select(Customer).where(Customer.email == user.email)
        ).scalar_one_or_none()
        
        if not customer:
            return jsonify({
                "message": "No customer account found for this user",
                "tickets": []
            }), 404
        
        # Get all tickets for this customer
        tickets = db.session.execute(
            select(Service_Tickets).where(Service_Tickets.customer_id == customer.id)
        ).scalars().all()
        
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "customer_id": customer.id,
            "tickets": service_tickets_schema.dump(tickets),
            "count": len(tickets)
        }), 200
    
    except Exception as e:
        return jsonify({
            "message": "Error retrieving tickets",
            "error": str(e)
        }), 500