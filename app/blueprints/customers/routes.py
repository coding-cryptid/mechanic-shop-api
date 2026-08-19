from .schemas import customer_schema, customers_schema
from flask import request, jsonify, current_app
from app.models import Customer, db
from sqlalchemy import select
from marshmallow import ValidationError
from . import customers_bp
from app.extensions import limiter, cache
from app.utils.util import encode_token, token_required

CUSTOMERS_PER_PAGE = 20

# POST /customers
@customers_bp.route('/', methods=['POST'])
def create_customer():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'JSON payload required'}), 400

        required_fields = ['name', 'email', 'phone_number']
        missing = [f for f in required_fields if not data.get(f)]
        
        if missing:
            return jsonify({
                'message': f'Missing required fields: {", ".join(missing)}'
            }), 400
        
        new_customer = Customer(
            name=data['name'],
            email=data['email'],
            phone_number=data['phone_number']
        )
        db.session.add(new_customer)
        db.session.commit()
        return customer_schema.jsonify(new_customer), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating customer', 'error': str(e)}), 500

# GET /customers w/ Pagination
@customers_bp.route('/', methods=['GET'])
@cache.cached(timeout=60)
def get_customers():
    try:
        page = request.args.get('page', 1, type=int)
        
        if page < 1:
            return jsonify({'message': 'Page number must be 1 or greater'}), 400
        
        query = select(Customer)
        paginated_query = db.session.execute(
            query.limit(CUSTOMERS_PER_PAGE).offset((page - 1) * CUSTOMERS_PER_PAGE)
        ).scalars()
        
        customers = paginated_query.all()
        
        total_count = db.session.execute(select(Customer)).scalars().all()
        total_customers = len(total_count)
        total_pages = (total_customers + CUSTOMERS_PER_PAGE - 1) // CUSTOMERS_PER_PAGE
        
        if page > total_pages and total_customers > 0:
            return jsonify({'message': f'Page {page} does not exist. Total pages: {total_pages}'}), 404
        
        return jsonify({
            'status': 'success',
            'customers': customers_schema.dump(customers),
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'total_customers': total_customers,
                'customers_per_page': CUSTOMERS_PER_PAGE,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Error retrieving customers', 'error': str(e)}), 500

# GET /customers/<id>
@customers_bp.route('/<int:id>', methods=['GET'])
@cache.cached(timeout=60)
def get_customer(id):
    try:
        customer = db.session.execute(db.select(Customer).where(Customer.id == id)).scalar_one_or_none()
        
        if not customer:
            return jsonify({'message': 'Customer not found'}), 404
        
        return customer_schema.jsonify(customer), 200
    
    except Exception as e:
        return jsonify({'message': 'Error retrieving customer', 'error': str(e)}), 500

# PUT /customers/<id>
@customers_bp.route('/<int:id>', methods=['PUT'])
def update_customer(id):
    try:
        customer = db.session.execute(db.select(Customer).where(Customer.id == id)).scalar_one_or_none()
        
        if not customer:
            return jsonify({'message': 'Customer not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'JSON payload required'}), 400
        
        # Check for required fields
        required_fields = ['name', 'email', 'phone_number']
        missing = [f for f in required_fields if not data.get(f)]
        
        if missing:
            return jsonify({
                'message': f'Missing required fields: {", ".join(missing)}'
            }), 400
        
        customer.name = data['name']
        customer.email = data['email']
        customer.phone_number = data['phone_number']
        db.session.commit()
        return customer_schema.jsonify(customer), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating customer', 'error': str(e)}), 500

# DELETE /customers/<id>
@customers_bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete_customer(user_id, id):
    try:
        customer = db.session.execute(db.select(Customer).where(Customer.id == id)).scalar_one_or_none()
        
        if not customer:
            return jsonify({'message': 'Customer not found'}), 404
        
        db.session.delete(customer)
        db.session.commit()
        return '', 204
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting customer', 'error': str(e)}), 500