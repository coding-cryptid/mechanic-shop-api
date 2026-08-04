from .schemas import service_tickets_schema, service_tickets_schema
from flask import request, jsonify
from app.models import Service_Tickets, db
from sqlalchemy import select
from marshmallow import ValidationError
from . import service_tickets_bp

# POST /service_tickets
@service_tickets_bp.route('/service_tickets', methods=['POST'])
def create_service_ticket():
    from flask import request, jsonify

    data = request.get_json()
    new_service_ticket = Service_Tickets(
        customer_id=data['customer_id'],
        vin=data['vin'],
        service_date=data['service_date'],
        service_description=data['service_description']
    )
    db.session.add(new_service_ticket)
    db.session.commit()
    return service_tickets_schema.jsonify(new_service_ticket), 201

# GET /service_tickets
@service_tickets_bp.route('/service_tickets', methods=['GET'])
def get_service_tickets():
    service_tickets = Service_Tickets.query.all()
    return service_tickets_schema.jsonify(service_tickets), 200

# GET /service_tickets/<id>
@service_tickets_bp.route('/service_tickets/<int:id>', methods=['GET'])
def get_service_ticket(id):
    service_ticket = Service_Tickets.query.get_or_404(id)
    return service_tickets_schema.jsonify(service_ticket), 200

# PUT /service_tickets/<id>
@service_tickets_bp.route('/service_tickets/<int:id>', methods=['PUT'])
def update_service_ticket(id):
    from flask import request, jsonify

    service_ticket = Service_Tickets.query.get_or_404(id)
    data = request.get_json()
    service_ticket.customer_id = data['customer_id']
    service_ticket.vin = data['vin']
    service_ticket.service_date = data['service_date']
    service_ticket.service_description = data['service_description']
    db.session.commit()
    return service_tickets_schema.jsonify(service_ticket), 200

# DELETE /service_tickets/<id>
@service_tickets_bp.route('/service_tickets/<int:id>', methods=['DELETE'])
def delete_service_ticket(id):
    service_ticket = Service_Tickets.query.get_or_404(id)
    db.session.delete(service_ticket)
    db.session.commit()
    return '', 204