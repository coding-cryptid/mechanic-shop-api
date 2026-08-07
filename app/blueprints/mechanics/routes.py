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
@limiter.limit("3 per hour")
def create_mechanic():
    from flask import request, jsonify

    data = request.get_json()
    new_mechanic = Mechanics(
        name=data['name'],
        email=data['email'],
        phone_number=data['phone_number'],
        salary=data['salary']
    )
    db.session.add(new_mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(new_mechanic), 201

# GET /mechanics
@mechanics_bp.route('/mechanics', methods=['GET'])
@cache.cached(timeout=60)
def get_mechanics():
    # mechanics = Mechanics.query.all()
    mechanics = db.session.execute(db.select(Mechanics)).scalars().all()
    return mechanics_schema.jsonify(mechanics), 200

# GET /mechanics/<id>
@mechanics_bp.route('/mechanics/<int:id>', methods=['GET'])
@cache.cached(timeout=60)
def get_mechanic(id):
    # mechanic = Mechanics.query.get_or_404(id)
    mechanic = db.session.execute(db.select(Mechanics).where(Mechanics.id == id)).scalar_one_or_none()
    return mechanic_schema.jsonify(mechanic), 200

# PUT /mechanics/<id>
@mechanics_bp.route('/mechanics/<int:id>', methods=['PUT'])
def update_mechanic(id):
    from flask import request, jsonify

    # mechanic = Mechanics.query.get_or_404(id)
    mechanic = db.session.execute(db.select(Mechanics).where(Mechanics.id == id)).scalar_one_or_none()
    data = request.get_json()
    mechanic.name = data['name']
    mechanic.email = data['email']
    mechanic.phone_number = data['phone_number']
    mechanic.salary = data['salary']
    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200

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
@mechanics_bp.route('/mechanics/<int:id>', methods=['DELETE'])
@token_required
@limiter.limit("3 per hour")
def delete_mechanic(id):
    mechanic = Mechanics.query.get_or_404(id)
    db.session.delete(mechanic)
    db.session.commit()
    return '', 204