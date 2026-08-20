from flask import request, jsonify
from sqlalchemy import select

from app.models import (
    Inventory,
    ServiceTicketInventory,
    Service_Tickets,
    db
)
from app.extensions import cache
from app.utils.util import token_required

from . import inventory_bp
from .schemas import (
    inventory_schema,
    inventories_schema,
    service_ticket_inventory_schema
)


# =========================================================
# INVENTORY CRUD
# Blueprint prefix is already /inventory
# These routes therefore become:
# /inventory/inventory/
# /inventory/inventory/<id>
# =========================================================


# POST /inventory/inventory/ - Create a new part
@inventory_bp.route('/inventory', methods=['POST'], strict_slashes=False)
def create_inventory():
    """Create a new inventory item (part)."""
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                'message': 'JSON payload required'
            }), 400

        if not data.get('name') or data.get('price') is None:
            return jsonify({
                'message': 'Name and price are required'
            }), 400

        try:
            price = float(data['price'])
        except (ValueError, TypeError):
            return jsonify({
                'message': 'Price must be a valid number'
            }), 400

        if price < 0:
            return jsonify({
                'message': 'Price cannot be negative'
            }), 400

        new_item = Inventory(
            name=data['name'],
            price=price
        )

        db.session.add(new_item)
        db.session.commit()

        # Clear inventory cache after creating
        cache.clear()

        return inventory_schema.jsonify(new_item), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Error creating inventory item',
            'error': str(e)
        }), 500


# GET /inventory/inventory/ - Get all parts
@inventory_bp.route('/inventory', methods=['GET'], strict_slashes=False)
def get_all_inventory():
    """Retrieve all inventory items."""
    try:
        items = db.session.execute(
            select(Inventory)
        ).scalars().all()

        return jsonify(
            inventories_schema.dump(items)
        ), 200

    except Exception as e:
        return jsonify({
            'message': 'Error retrieving inventory',
            'error': str(e)
        }),


# GET /inventory/inventory/<id> - Get a single part
@inventory_bp.route('/inventory/<int:id>', methods=['GET'])
@cache.cached(timeout=60)
def get_inventory(id):
    """Retrieve a single inventory item by ID."""
    try:
        query = select(Inventory).where(Inventory.id == id)
        item = db.session.execute(query).scalar_one_or_none()

        if not item:
            return jsonify({
                'message': 'Inventory item not found'
            }), 404

        return inventory_schema.jsonify(item), 200

    except Exception as e:
        return jsonify({
            'message': 'Error retrieving inventory item',
            'error': str(e)
        }), 500


# PUT /inventory/inventory/<id> - Update a part
@inventory_bp.route('/inventory/<int:id>', methods=['PUT'])
def update_inventory(id):
    """Update an inventory item."""
    try:
        query = select(Inventory).where(Inventory.id == id)
        item = db.session.execute(query).scalar_one_or_none()

        if not item:
            return jsonify({
                'message': 'Inventory item not found'
            }), 404

        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                'message': 'JSON payload required'
            }), 400

        if 'name' in data:
            if not data['name']:
                return jsonify({
                    'message': 'Name cannot be empty'
                }), 400

            item.name = data['name']

        if 'price' in data:
            try:
                price = float(data['price'])
            except (ValueError, TypeError):
                return jsonify({
                    'message': 'Price must be a valid number'
                }), 400

            if price < 0:
                return jsonify({
                    'message': 'Price cannot be negative'
                }), 400

            item.price = price

        db.session.commit()

        # Clear cached inventory GET responses
        cache.clear()

        return inventory_schema.jsonify(item), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Error updating inventory item',
            'error': str(e)
        }), 500


# DELETE /inventory/inventory/<id> - Delete a part
@inventory_bp.route('/inventory/<int:id>', methods=['DELETE'])
@token_required
def delete_inventory(user_id, id):
    """Delete an inventory item."""
    try:
        query = select(Inventory).where(Inventory.id == id)
        item = db.session.execute(query).scalar_one_or_none()

        if not item:
            return jsonify({
                'message': 'Inventory item not found'
            }), 404

        db.session.delete(item)
        db.session.commit()

        cache.clear()

        return jsonify({
            'message': 'Inventory item deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Error deleting inventory item',
            'error': str(e)
        }), 500


# =========================================================
# SERVICE TICKET + INVENTORY ROUTES
#
# Blueprint prefix: /inventory
#
# Full routes:
# /inventory/inventory/service-tickets/<ticket_id>/add-part
# /inventory/inventory/service-tickets/<ticket_id>/parts
# /inventory/inventory/service-tickets/<ticket_id>/parts/<inventory_id>
# =========================================================


# POST - Add a part to a service ticket
@inventory_bp.route(
    '/inventory/service-tickets/<int:ticket_id>/add-part',
    methods=['POST']
)
def add_part_to_ticket(ticket_id):
    """
    Add an inventory item to a service ticket.

    Expected JSON:
    {
        "inventory_id": 5,
        "quantity": 2
    }
    """
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                'message': 'JSON payload required'
            }), 400

        inventory_id = data.get('inventory_id')
        quantity = data.get('quantity', 1)

        if not inventory_id:
            return jsonify({
                'message': 'inventory_id is required'
            }), 400

        if not isinstance(quantity, int) or isinstance(quantity, bool):
            return jsonify({
                'message': 'Quantity must be a positive integer'
            }), 400

        if quantity < 1:
            return jsonify({
                'message': 'Quantity must be a positive integer'
            }), 400

        # Verify ticket exists
        ticket_query = select(Service_Tickets).where(
            Service_Tickets.id == ticket_id
        )
        ticket = db.session.execute(
            ticket_query
        ).scalar_one_or_none()

        if not ticket:
            return jsonify({
                'message': 'Service ticket not found'
            }), 404

        # Verify inventory item exists
        inventory_query = select(Inventory).where(
            Inventory.id == inventory_id
        )
        inventory = db.session.execute(
            inventory_query
        ).scalar_one_or_none()

        if not inventory:
            return jsonify({
                'message': 'Inventory item not found'
            }), 404

        # Check whether the part is already on the ticket
        existing = db.session.execute(
            select(ServiceTicketInventory).where(
                ServiceTicketInventory.service_ticket_id == ticket_id,
                ServiceTicketInventory.inventory_id == inventory_id
            )
        ).scalar_one_or_none()

        if existing:
            existing.quantity += quantity
            final_quantity = existing.quantity
        else:
            new_link = ServiceTicketInventory(
                service_ticket_id=ticket_id,
                inventory_id=inventory_id,
                quantity=quantity
            )
            db.session.add(new_link)
            final_quantity = quantity

        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': (
                f'Added {quantity} unit(s) of '
                f'"{inventory.name}" to ticket #{ticket_id}'
            ),
            'ticket_id': ticket_id,
            'inventory_id': inventory_id,
            'quantity': final_quantity
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Error adding part to ticket',
            'error': str(e)
        }), 500


# GET - Get all parts on a service ticket
@inventory_bp.route(
    '/inventory/service-tickets/<int:ticket_id>/parts',
    methods=['GET']
)
def get_ticket_parts(ticket_id):
    try:
        parts = db.session.execute(
            select(ServiceTicketInventory).where(
                ServiceTicketInventory.service_ticket_id == ticket_id
            )
        ).scalars().all()

        # If parts exist, this is a valid ticket for purposes of this endpoint
        if parts:
            parts_data = [
                {
                    'inventory_id': part.inventory_id,
                    'name': part.inventory.name,
                    'price': part.inventory.price,
                    'quantity': part.quantity,
                    'total_cost': part.inventory.price * part.quantity
                }
                for part in parts
            ]

            return jsonify({
                'status': 'success',
                'ticket_id': ticket_id,
                'parts': parts_data,
                'part_count': len(parts_data)
            }), 200

        # No parts found. Check whether the ticket itself exists.
        ticket = db.session.execute(
            select(Service_Tickets).where(
                Service_Tickets.id == ticket_id
            )
        ).scalar_one_or_none()

        if not ticket:
            return jsonify({
                'message': 'Service ticket not found'
            }), 404

        # Valid ticket, just no parts
        return jsonify({
            'status': 'success',
            'ticket_id': ticket_id,
            'parts': [],
            'part_count': 0
        }), 200

    except Exception as e:
        return jsonify({
            'message': 'Error retrieving ticket parts',
            'error': str(e)
        }), 500

# DELETE - Remove a part from a service ticket
@inventory_bp.route(
    '/inventory/service-tickets/<int:ticket_id>/parts/<int:inventory_id>',
    methods=['DELETE']
)
def remove_part_from_ticket(ticket_id, inventory_id):
    try:
        link = db.session.execute(
            select(ServiceTicketInventory).where(
                ServiceTicketInventory.service_ticket_id == ticket_id,
                ServiceTicketInventory.inventory_id == inventory_id
            )
        ).scalar_one_or_none()

        if not link:
            return jsonify({
                'message': 'Part not found on this ticket'
            }), 404

        db.session.delete(link)
        db.session.commit()

        return jsonify({
            'message': f'Part removed from ticket #{ticket_id}'
        }), 200

    except Exception as e:
        db.session.rollback()

        return jsonify({
            'message': 'Error removing part from ticket',
            'error': str(e)
        }), 500