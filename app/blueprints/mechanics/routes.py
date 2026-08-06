from .schemas import mechanic_schema, mechanics_schema
from flask import request, jsonify
from app.models import Mechanics, db
from sqlalchemy import select
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
    mechanics = Mechanics.query.all()
    return mechanics_schema.jsonify(mechanics), 200

# GET /mechanics/<id>
@mechanics_bp.route('/mechanics/<int:id>', methods=['GET'])
@cache.cached(timeout=60)
def get_mechanic(id):
    mechanic = Mechanics.query.get_or_404(id)
    return mechanic_schema.jsonify(mechanic), 200

# PUT /mechanics/<id>
@mechanics_bp.route('/mechanics/<int:id>', methods=['PUT'])
def update_mechanic(id):
    from flask import request, jsonify

    mechanic = Mechanics.query.get_or_404(id)
    data = request.get_json()
    mechanic.name = data['name']
    mechanic.email = data['email']
    mechanic.phone_number = data['phone_number']
    mechanic.salary = data['salary']
    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200

# DELETE /mechanics/<id>
@mechanics_bp.route('/mechanics/<int:id>', methods=['DELETE'])
@limiter.limit("3 per hour")
def delete_mechanic(id):
    mechanic = Mechanics.query.get_or_404(id)
    db.session.delete(mechanic)
    db.session.commit()
    return '', 204