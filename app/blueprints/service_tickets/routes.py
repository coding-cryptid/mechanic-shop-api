from datetime import datetime

from flask import request, jsonify
from sqlalchemy import select

from app.models import Service_Tickets, Mechanics, db
from .schemas import service_tickets_schema, service_ticket_schema
from . import service_tickets_bp
from app.extensions import cache


DATE_FORMATS = [
    '%m/%d/%Y',
    '%m/%d/%y',
    '%Y-%m-%d',
    '%d/%m/%Y'
]

def parse_service_date(date_string):
    """
    Convert a date string into a Python datetime.date object.

    Accepted formats:
    MM/DD/YYYY
    MM/DD/YY
    YYYY-MM-DD
    DD/MM/YYYY
    """
    if not isinstance(date_string, str):
        return None

    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(date_string, fmt).date()
        except ValueError:
            continue

    return None


# ============================================================
# POST /service_tickets
# Create a new service ticket
# ============================================================

@service_tickets_bp.route('/service_tickets', methods=['POST'])
def create_service_ticket():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'message': 'JSON payload required'
            }), 400

        required_fields = [
            'customer_id',
            'vin',
            'service_date',
            'service_description'
        ]

        missing_fields = [
            field for field in required_fields
            if field not in data
        ]

        if missing_fields:
            return jsonify({
                'message': 'Missing required fields',
                'fields': missing_fields
            }), 400

        service_date = parse_service_date(
            data['service_date']
        )

        if service_date is None:
            return jsonify({
                'message': (
                    'Invalid date format. Use '
                    'MM/DD/YYYY, MM/DD/YY, '
                    'YYYY-MM-DD, or DD/MM/YYYY'
                )
            }), 400

        new_service_ticket = Service_Tickets(
            customer_id=data['customer_id'],
            vin=data['vin'],
            service_date=service_date,
            service_description=data['service_description']
        )

        db.session.add(new_service_ticket)
        db.session.commit()

        return service_ticket_schema.jsonify(
            new_service_ticket
        ), 201

    except Exception as e:
        db.session.rollback()

        return jsonify({
            'message': 'Error creating service ticket',
            'error': str(e),
            'type': type(e).__name__
        }), 500


# ============================================================
# GET /service_tickets
# Get all service tickets
# ============================================================

@service_tickets_bp.route('/service_tickets', methods=['GET'])
@cache.cached(timeout=60)
def get_service_tickets():
    try:
        service_tickets = db.session.execute(
            select(Service_Tickets)
        ).scalars().all()

        return service_tickets_schema.jsonify(
            service_tickets
        ), 200

    except Exception as e:
        return jsonify({
            'message': 'Error retrieving service tickets',
            'error': str(e)
        }), 500


# ============================================================
# GET /service_tickets/<id>
# Get one service ticket
# ============================================================

@service_tickets_bp.route(
    '/service_tickets/<int:id>',
    methods=['GET']
)
@cache.cached(timeout=60)
def get_service_ticket(id):
    try:
        service_ticket = db.session.execute(
            select(Service_Tickets).where(
                Service_Tickets.id == id
            )
        ).scalar_one_or_none()

        if not service_ticket:
            return jsonify({
                'message': 'Service ticket not found'
            }), 404

        return service_ticket_schema.jsonify(
            service_ticket
        ), 200

    except Exception as e:
        return jsonify({
            'message': 'Error retrieving service ticket',
            'error': str(e)
        }), 500


# ============================================================
# PUT /service_tickets/<id>
# Update an existing service ticket
# ============================================================

@service_tickets_bp.route(
    '/service_tickets/<int:id>',
    methods=['PUT']
)
def update_service_ticket(id):
    try:
        service_ticket = db.session.execute(
            select(Service_Tickets).where(
                Service_Tickets.id == id
            )
        ).scalar_one_or_none()

        if not service_ticket:
            return jsonify({
                'message': 'Service ticket not found'
            }), 404

        data = request.get_json()

        if not data:
            return jsonify({
                'message': 'JSON payload required'
            }), 400

        required_fields = [
            'customer_id',
            'vin',
            'service_date',
            'service_description'
        ]

        missing_fields = [
            field for field in required_fields
            if field not in data
        ]

        if missing_fields:
            return jsonify({
                'message': 'Missing required fields',
                'fields': missing_fields
            }), 400

        service_date = parse_service_date(
            data['service_date']
        )

        if service_date is None:
            return jsonify({
                'message': (
                    'Invalid date format. Use '
                    'MM/DD/YYYY, MM/DD/YY, '
                    'YYYY-MM-DD, or DD/MM/YYYY'
                )
            }), 400

        service_ticket.customer_id = data['customer_id']
        service_ticket.vin = data['vin']
        service_ticket.service_date = service_date
        service_ticket.service_description = (
            data['service_description']
        )

        db.session.commit()

        return service_ticket_schema.jsonify(
            service_ticket
        ), 200

    except Exception as e:
        db.session.rollback()

        return jsonify({
            'message': 'Error updating service ticket',
            'error': str(e),
            'type': type(e).__name__
        }), 500


# ============================================================
# PUT /service_tickets/<ticket_id>/edit
# Add/remove multiple mechanics
# ============================================================

@service_tickets_bp.route(
    '/service_tickets/<int:ticket_id>/edit',
    methods=['PUT']
)
def edit_ticket_mechanics(ticket_id):
    """
    Expected JSON:

    {
        "add_ids": [1, 2, 3],
        "remove_ids": [4, 5]
    }
    """

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'message': 'JSON payload required'
            }), 400

        add_ids = data.get('add_ids', [])
        remove_ids = data.get('remove_ids', [])

        if not isinstance(add_ids, list):
            return jsonify({
                'message': 'add_ids must be a list'
            }), 400

        if not isinstance(remove_ids, list):
            return jsonify({
                'message': 'remove_ids must be a list'
            }), 400

        ticket = db.session.execute(
            select(Service_Tickets).where(
                Service_Tickets.id == ticket_id
            )
        ).scalar_one_or_none()

        if not ticket:
            return jsonify({
                'message': 'Ticket not found'
            }), 404

        # Remove mechanics
        for mechanic_id in remove_ids:

            mechanic = db.session.execute(
                select(Mechanics).where(
                    Mechanics.id == mechanic_id
                )
            ).scalar_one_or_none()

            if not mechanic:
                return jsonify({
                    'message': (
                        f'Mechanic {mechanic_id} '
                        'not found'
                    )
                }), 404

            if mechanic in ticket.mechanics:
                ticket.mechanics.remove(mechanic)

        # Add mechanics
        for mechanic_id in add_ids:

            mechanic = db.session.execute(
                select(Mechanics).where(
                    Mechanics.id == mechanic_id
                )
            ).scalar_one_or_none()

            if not mechanic:
                return jsonify({
                    'message': (
                        f'Mechanic {mechanic_id} '
                        'not found'
                    )
                }), 404

            if mechanic not in ticket.mechanics:
                ticket.mechanics.append(mechanic)

        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Mechanics updated successfully',
            'ticket': service_ticket_schema.dump(ticket)
        }), 200

    except Exception as e:
        db.session.rollback()

        return jsonify({
            'message': 'Error updating ticket mechanics',
            'error': str(e),
            'type': type(e).__name__
        }), 500