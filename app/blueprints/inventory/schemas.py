from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from app.models import Inventory, ServiceTicketInventory
from app.extensions import ma


class InventorySchema(ma.SQLAlchemyAutoSchema):
    """Schema for single Inventory item"""
    class Meta:
        model = Inventory
        load_instance = True

    id = auto_field()
    name = auto_field()
    price = auto_field()


class InventoriesSchema(ma.SQLAlchemyAutoSchema):
    """Schema for multiple Inventory items"""
    class Meta:
        model = Inventory
        load_instance = True
        many = True

    id = auto_field()
    name = auto_field()
    price = auto_field()


class ServiceTicketInventorySchema(ma.SQLAlchemyAutoSchema):
    """Schema for junction table (part + quantity on a ticket)"""
    class Meta:
        model = ServiceTicketInventory
        load_instance = True

    service_ticket_id = auto_field()
    inventory_id = auto_field()
    quantity = auto_field()


inventory_schema = InventorySchema()
inventories_schema = InventoriesSchema()
service_ticket_inventory_schema = ServiceTicketInventorySchema()