from flask import request, jsonify
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models import Customer, db
from app.utils.util import token_required

from . import customers_bp
from .schemas import customer_schema, customers_schema


CUSTOMERS_PER_PAGE = 20


# ============================================================
# POST /customers/
# Create customer
# ============================================================

@customers_bp.route('/', methods=['POST'])
def create_customer():
    try:
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                'message': 'JSON payload required'
            }), 400

        required_fields = [
            'name',
            'email',
            'phone_number'
        ]

        missing = [
            field
            for field in required_fields
            if not data.get(field)
        ]

        if missing:
            return jsonify({
                'message': (
                    f'Missing required fields: {", ".join(missing)}'
                )
            }), 400

        new_customer = Customer(
            name=data['name'],
            email=data['email'],
            phone_number=data['phone_number']
        )

        db.session.add(new_customer)
        db.session.commit()

        return customer_schema.jsonify(new_customer), 201

    except IntegrityError as e:
        db.session.rollback()
        if 'email' in str(e):
            return jsonify({
                'message': 'Email already exists'
            }), 409
        return jsonify({
            'message': 'Error updating customer',
            'error': str(e)
        }), 400
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Error updating customer',
            'error': str(e)
        }), 500


# ============================================================
# GET /customers/
# Get customers with pagination
# ============================================================

@customers_bp.route('/', methods=['GET'])
def get_customers():
    try:
        # Do NOT use:
        #
        # request.args.get('page', 1, type=int)
        #
        # because "abc" can fall back to the default value.

        page_value = request.args.get('page')

        if page_value is None:
            page = 1
        else:
            try:
                page = int(page_value)
            except (ValueError, TypeError):
                return jsonify({
                    'message': 'Page number must be a valid integer'
                }), 400

        if page < 1:
            return jsonify({
                'message': 'Page number must be 1 or greater'
            }), 400

        query = (
            select(Customer)
            .limit(CUSTOMERS_PER_PAGE)
            .offset(
                (page - 1) * CUSTOMERS_PER_PAGE
            )
        )

        customers = db.session.execute(
            query
        ).scalars().all()

        # Get total number of customers
        total_customers = len(
            db.session.execute(
                select(Customer)
            ).scalars().all()
        )

        total_pages = (
            total_customers
            + CUSTOMERS_PER_PAGE
            - 1
        ) // CUSTOMERS_PER_PAGE

        if (
            total_customers > 0
            and page > total_pages
        ):
            return jsonify({
                'message': (
                    f'Page {page} does not exist. '
                    f'Total pages: {total_pages}'
                )
            }), 404

        return jsonify({
            'status': 'success',

            'customers': customers_schema.dump(
                customers
            ),

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
        return jsonify({
            'message': 'Error retrieving customers',
            'error': str(e)
        }), 500


# ============================================================
# GET /customers/<id>
# Get one customer
# ============================================================

@customers_bp.route('/<int:id>', methods=['GET'])
def get_customer(id):
    try:
        customer = db.session.execute(
            select(Customer).where(
                Customer.id == id
            )
        ).scalar_one_or_none()

        if not customer:
            return jsonify({
                'message': 'Customer not found'
            }), 404

        return customer_schema.jsonify(
            customer
        ), 200

    except Exception as e:
        return jsonify({
            'message': 'Error retrieving customer',
            'error': str(e)
        }), 500


# ============================================================
# PUT /customers/<id>
# Update customer
# ============================================================

@customers_bp.route('/<int:id>', methods=['PUT'])
def update_customer(id):
    try:
        customer = db.session.execute(
            select(Customer).where(
                Customer.id == id
            )
        ).scalar_one_or_none()

        if not customer:
            return jsonify({
                'message': 'Customer not found'
            }), 404

        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                'message': 'JSON payload required'
            }), 400

        required_fields = [
            'name',
            'email',
            'phone_number'
        ]

        missing = [
            field
            for field in required_fields
            if not data.get(field)
        ]

        if missing:
            return jsonify({
                'message': (
                    f'Missing required fields: '
                    f'{", ".join(missing)}'
                )
            }), 400

        customer.name = data['name']
        customer.email = data['email']
        customer.phone_number = data['phone_number']

        db.session.commit()

        # Refresh the SQLAlchemy object after commit
        db.session.refresh(customer)

        return customer_schema.jsonify(
            customer
        ), 200

    except IntegrityError as e:
        db.session.rollback()
        if 'email' in str(e):
            return jsonify({
                'message': 'Email already exists'
            }), 409
        return jsonify({
            'message': 'Error updating customer',
            'error': str(e)
        }), 400
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Error updating customer',
            'error': str(e)
        }), 500

        # Keep this temporarily.
        # If the test still returns 500, this tells us exactly why.
        print(
            "UPDATE CUSTOMER ERROR:",
            repr(e)
        )

        return jsonify({
            'message': 'Error updating customer',
            'error': str(e)
        }), 500


# ============================================================
# DELETE /customers/<id>
# Delete customer
# ============================================================

@customers_bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete_customer(user_id, id):
    try:
        customer = db.session.execute(
            select(Customer).where(
                Customer.id == id
            )
        ).scalar_one_or_none()

        if not customer:
            return jsonify({
                'message': 'Customer not found'
            }), 404

        db.session.delete(customer)
        db.session.commit()

        return '', 204

    except Exception as e:
        db.session.rollback()

        return jsonify({
            'message': 'Error deleting customer',
            'error': str(e)
        }), 500