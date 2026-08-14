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

# GET /customers w/ Pagination
@customers_bp.route('/', methods=['GET'])
@cache.cached(timeout=60)
def get_customers():
    """
    Get all customers with pagination (20 per page)
    
    Query parameters:
    - page: page number (default: 1)
    
    Example: GET /customers?page=1
    """
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
@customers_bp.route('/customers/<int:id>', methods=['GET'])
@cache.cached(timeout=60)
def get_customer(id):
    # customer = Customer.query.get_or_404(id)
    customer = db.session.execute(db.select(Customer).where(Customer.id == id)).scalar_one_or_none()
    return customer_schema.jsonify(customer), 200

# PUT /customers/<id>
@customers_bp.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    from flask import request, jsonify

    # customer = Customer.query.get_or_404(id)
    customer = db.session.execute(db.select(Customer).where(Customer.id == id)).scalar_one_or_none()
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