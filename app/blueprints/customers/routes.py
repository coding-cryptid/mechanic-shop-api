from .schemas import customer_schema, customers_schema
from flask import request, jsonify
from app.models import Customer, db
from sqlalchemy import select
from marshmallow import ValidationError
from . import customers_bp
from extensions import limiter, cache
from app.utils.util import encode_token, token_required

# POST /customers
@customers_bp.route('/customers', methods=['POST'])
def login():
    try:
        credentials = request.json
        username = credentails['email']
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

def create_customer():
    from flask import request, jsonify

    data = request.get_json()
    new_customer = Customer(
        name=data['name'],
        email=data['email'],
        phone_number=data['phone_number']
    )
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201

# GET /customers
@customers_bp.route('/customers', methods=['GET'])
@cache.cached(timeout=60)
def get_customers():
    customers = Customer.query.all()
    return customers_schema.jsonify(customers), 200

# GET /customers/<id>
@customers_bp.route('/customers/<int:id>', methods=['GET'])
@cache.cached(timeout=60)
def get_customer(id):
    customer = Customer.query.get_or_404(id)
    return customer_schema.jsonify(customer), 200

# PUT /customers/<id>
@customers_bp.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    from flask import request, jsonify

    customer = Customer.query.get_or_404(id)
    data = request.get_json()
    customer.name = data['name']
    customer.email = data['email']
    customer.phone_number = data['phone_number']
    db.session.commit()
    return customer_schema.jsonify(customer), 200

# DELETE /customers/<id>
@customers_bp.route('/customers/<int:id>', methods=['DELETE'])
@token_required
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return '', 204