from .schemas import service_tickets_schema, service_ticket_schema
from flask import request, jsonify
from app.models import Service_Tickets, db, Mechanics
from sqlalchemy import select
from marshmallow import ValidationError
from . import service_tickets_bp
from app.extensions import limiter, cache

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
@cache.cached(timeout=60)
def get_service_tickets():
    # service_tickets = Service_Tickets.query.all()
    service_tickets = db.session.execute(db.select(Service_Tickets)).scalars().all()
    return service_tickets_schema.jsonify(service_tickets), 200

# GET /service_tickets/<id>
@service_tickets_bp.route('/service_tickets/<int:id>', methods=['GET'])
@cache.cached(timeout=60)
def get_service_ticket(id):
    # service_ticket = Service_Tickets.query.get_or_404(id)
    service_ticket = db.session.execute(db.select(Service_Tickets).where(Service_Tickets.id == id)).scalar_one_or_none()
    return service_tickets_schema.jsonify(service_ticket), 200

# PUT /service_tickets/<id>
@service_tickets_bp.route('/service_tickets/<int:id>', methods=['PUT'])
def update_service_ticket(id):
    from flask import request, jsonify

    # service_ticket = Service_Tickets.query.get_or_404(id)
    service_ticket = db.session.execute(db.select(Service_Tickets).where(Service_Tickets.id == id)).scalar_one_or_none()
    data = request.get_json()
    service_ticket.customer_id = data['customer_id']
    service_ticket.vin = data['vin']
    service_ticket.service_date = data['service_date']
    service_ticket.service_description = data['service_description']
    db.session.commit()
    return service_tickets_schema.jsonify(service_ticket), 200


# PUT /service_tickets/<ticket_id>/edit
# Add and remove multiple mechanics from a ticket
@service_tickets_bp.route('/service_tickets/<int:ticket_id>/edit', methods=['PUT'])
def edit_ticket_mechanics(ticket_id):
    """
    Add and remove mechanics from a ticket in one request
    
    Expected JSON:
    {
        "add_ids": [1, 2, 3],
        "remove_ids": [4, 5]
    }
    """
    try:
        data = request.get_json()
        add_ids = data.get('add_ids', [])
        remove_ids = data.get('remove_ids', [])

        if not isinstance(add_ids, list) or not isinstance(remove_ids, list):
            return jsonify({'message': 'add_ids and remove_ids must be lists'}), 400
        
        ticket = db.session.execute(
            select(Service_Tickets).where(Service_Tickets.id == ticket_id)
        ).scalar_one_or_none()
        
        if not ticket:
            return jsonify({'message': 'Ticket not found'}), 404
        
        for mechanic_id in remove_ids:
            mechanic = db.session.execute(
                select(Mechanics).where(Mechanics.id == mechanic_id)
            ).scalar_one_or_none()
            
            if mechanic and mechanic in ticket.mechanics:
                ticket.mechanics.remove(mechanic)
            elif not mechanic:
                return jsonify({'message': f'Mechanic {mechanic_id} not found'}), 404
        
        for mechanic_id in add_ids:
            mechanic = db.session.execute(
                select(Mechanics).where(Mechanics.id == mechanic_id)
            ).scalar_one_or_none()
            
            if not mechanic:
                return jsonify({'message': f'Mechanic {mechanic_id} not found'}), 404
            
            if mechanic not in ticket.mechanics:
                ticket.mechanics.append(mechanic)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Mechanics updated successfully',
            'ticket': service_ticket_schema.dump(ticket)
        }), 200
        
    except TypeError:
        return jsonify({'message': 'Invalid payload, expecting JSON'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating ticket mechanics', 'error': str(e)}), 500

# # Assign a mechanic to a ticket
# @service_tickets_bp.route('/<ticket_id>/assign-mechanic/<mechanic_id>', methods=['PUT'])
# def assign_mechanic(ticket_id, mechanic_id):
#     # ticket = Service_Tickets.query.get_or_404(ticket_id)
#     ticket = db.session.execute(db.select(Service_Tickets).where(Service_Tickets.id == ticket_id)).scalar_one_or_none()
#     # mechanic = Mechanics.query.get_or_404(mechanic_id)
#     mechanic = db.session.execute(db.select(Mechanics).where(Mechanics.id == mechanic_id)).scalar_one_or_none()

#     if mechanic not in ticket.mechanics:
#         ticket.mechanics.append(mechanic)
#         db.session.commit()
#         return jsonify({'message': f'Mechanic {mechanic_id} assigned to ticket {ticket_id}'}), 200
    
#     return jsonify({'message': 'Mechanic already assigned'}), 400

# # Remove a mechanic from a ticket
# @service_tickets_bp.route('/<ticket_id>/remove-mechanic/<mechanic_id>', methods=['PUT'])
# def remove_mechanic(ticket_id, mechanic_id):
#     # ticket = Service_Tickets.query.get_or_404(ticket_id)
#     ticket = db.session.execute(db.select(Service_Tickets).where(Service_Tickets.id == ticket_id)).scalar_one_or_none()
#     # mechanic = Mechanics.query.get_or_404(mechanic_id)
#     mechanic = db.session.execute(db.select(Mechanics).where(Mechanics.id == mechanic_id)).scalar_one_or_none()

#     if mechanic in ticket.mechanics:
#         ticket.mechanics.remove(mechanic)
#         db.session.commit()
#         return jsonify({'message': f'Mechanic {mechanic_id} removed from ticket {ticket_id}'}), 200
    
#     return jsonify({'message': 'Mechanic not assigned to this ticket'}), 400