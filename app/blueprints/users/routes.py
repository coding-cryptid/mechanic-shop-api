from flask import request, jsonify
from sqlalchemy import select
from werkzeug.security import check_password_hash
from app.models import Users, Customer, db
from app.utils.util import encode_token
from . import users_bp
from .schemas import user_schema
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
            "token": token,
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
def get_my_tickets():
    """
    Get all service tickets for the authenticated user
    Requires valid JWT token in Authorization header
    """
    try:
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({"message": "Missing Authorization header"}), 401
        
        parts = auth_header.split()
        
        if len(parts) != 2 or parts[0] != 'Bearer':
            return jsonify({"message": "Invalid Authorization header format"}), 401
        
        token = parts[1]
        
        # Decode token to get user_id
        from app.utils.util import decode_token
        
        try:
            user_id = decode_token(token)
        except Exception:
            return jsonify({"message": "Invalid or expired token"}), 401
        
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
                "message": "No customer found for this user",
                "tickets": []
            }), 200
        
        # Get all tickets for this customer
        from app.models import Service_Tickets
        from .schemas import service_tickets_schema
        
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