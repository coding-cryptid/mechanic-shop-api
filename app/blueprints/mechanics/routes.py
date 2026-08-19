from app.utils.util import token_required
from .schemas import mechanic_schema, mechanics_schema
from flask import request, jsonify
from app.models import Mechanics, Service_Tickets, db
from sqlalchemy import desc, func, select
from marshmallow import ValidationError
from . import mechanics_bp
from app.extensions import limiter, cache

# POST /mechanics
@mechanics_bp.route('/mechanics', methods=['POST'])
@limiter.limit("6 per hour")
def create_mechanic():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'JSON payload required'}), 400
        
        # Validate all required fields
        required_fields = ['name', 'email', 'phone_number', 'salary']
        missing = [f for f in required_fields if not data.get(f)]
        
        if missing:
            return jsonify({
                'message': f'Missing required fields: {", ".join(missing)}'
            }), 400
        
        # Validate salary is numeric
        try:
            salary = int(data['salary'])
        except (ValueError, TypeError):
            return jsonify({'message': 'Salary must be a valid integer'}), 400
        
        new_mechanic = Mechanics(
            name=data['name'],
            email=data['email'],
            phone_number=data['phone_number'],
            salary=salary
        )
        db.session.add(new_mechanic)
        db.session.commit()
        return mechanic_schema.jsonify(new_mechanic), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating mechanic', 'error': str(e)}), 500

# GET /mechanics
@mechanics_bp.route('/mechanics', methods=['GET'])
@cache.cached(timeout=60)
def get_mechanics():
    mechanics = db.session.execute(db.select(Mechanics)).scalars().all()
    return mechanics_schema.jsonify(mechanics), 200

# GET /mechanics/<id>
@mechanics_bp.route('/mechanics/<int:id>', methods=['GET'])
@cache.cached(timeout=60)
def get_mechanic(id):
    try:
        mechanic = db.session.execute(db.select(Mechanics).where(Mechanics.id == id)).scalar_one_or_none()
        
        if not mechanic:
            return jsonify({'message': 'Mechanic not found'}), 404
        
        return mechanic_schema.jsonify(mechanic), 200
    
    except Exception as e:
        return jsonify({'message': 'Error retrieving mechanic', 'error': str(e)}), 500

# PUT /mechanics/<id>
@mechanics_bp.route('/mechanics/<int:id>', methods=['PUT'])
def update_mechanic(id):
    try:
        mechanic = db.session.execute(db.select(Mechanics).where(Mechanics.id == id)).scalar_one_or_none()
        
        if not mechanic:
            return jsonify({'message': 'Mechanic not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'JSON payload required'}), 400
        
        # Validate all required fields
        required_fields = ['name', 'email', 'phone_number', 'salary']
        missing = [f for f in required_fields if not data.get(f)]
        
        if missing:
            return jsonify({
                'message': f'Missing required fields: {", ".join(missing)}'
            }), 400
        
        # Validate salary is numeric
        try:
            salary = int(data['salary'])
        except (ValueError, TypeError):
            return jsonify({'message': 'Salary must be a valid integer'}), 400
        
        mechanic.name = data['name']
        mechanic.email = data['email']
        mechanic.phone_number = data['phone_number']
        mechanic.salary = salary
        db.session.commit()
        return mechanic_schema.jsonify(mechanic), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating mechanic', 'error': str(e)}), 500

# GET /mechanics/leaderboard
# Mechanics ranked by most tickets worked on
@mechanics_bp.route('/mechanics/leaderboard', methods=['GET'])
@cache.cached(timeout=300)
def get_mechanics_leaderboard():
    """
    Get all mechanics ranked by number of tickets they've worked on
    Returns mechanics in descending order (most tickets first)
    """
    try:
        query = select(
            Mechanics,
            func.count(Service_Tickets.id).label('ticket_count')
        ).outerjoin(
            Mechanics.service_tickets
        ).group_by(
            Mechanics.id
        ).order_by(
            desc('ticket_count')
        )
        
        result = db.session.execute(query).all()
        
        leaderboard = []
        for mechanic, ticket_count in result:
            mechanic_data = mechanic_schema.dump(mechanic)
            mechanic_data['tickets_completed'] = ticket_count
            leaderboard.append(mechanic_data)
        
        return jsonify({
            'status': 'success',
            'leaderboard': leaderboard,
            'total_mechanics': len(leaderboard)
        }), 200
        
    except Exception as e:
        return jsonify({
            'message': 'Error retrieving mechanics leaderboard',
            'error': str(e)
        }), 500

# DELETE /mechanics/<id>
# FIX: Added user_id parameter from @token_required decorator
@mechanics_bp.route('/mechanics/<int:id>', methods=['DELETE'])
@token_required
@limiter.limit("3 per hour")
def delete_mechanic(user_id, id):
    try:
        mechanic = db.session.execute(db.select(Mechanics).where(Mechanics.id == id)).scalar_one_or_none()
        
        if not mechanic:
            return jsonify({'message': 'Mechanic not found'}), 404
        
        db.session.delete(mechanic)
        db.session.commit()
        return '', 204
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting mechanic', 'error': str(e)}), 500