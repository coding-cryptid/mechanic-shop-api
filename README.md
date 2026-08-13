# Mechanic Shop API - Mechanic & Service Ticket Blueprints Implementation

## Overview

This phase extends the **Mechanic Shop REST API** by implementing two critical resource blueprints: **Mechanic** and **Service Ticket**. Following the Application Factory Pattern established with the Customer blueprint, we'll create parallel folder structures, Marshmallow schemas, and full CRUD routes for each resource.

**What we're adding:**
- Mechanic blueprint with complete CRUD operations
- Service Ticket blueprint with creation, assignment, and removal of mechanics
- Marshmallow schemas for data validation and serialization
- Comprehensive Postman collection for endpoint testing

---

## Project Structure

### Current State
```
mechanic-shop-api/
├── app/
│   ├── __init__.py                 # Application Factory
│   ├── blueprints/
│   │   └── customers/              # ✅ Already completed
│   │       ├── __init__.py
│   │       ├── routes.py
│   │       └── schemas.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── customer.py
│   │   ├── mechanic.py             # Model exists, now adding blueprint
│   │   ├── service_ticket.py        # Model exists, now adding blueprint
│   │   └── ... (other models)
│   └── extensions.py
├── main.py
└── requirements.txt
```

### After Implementation
```
mechanic-shop-api/
├── app/
│   ├── __init__.py                 # Register all blueprints here
│   ├── blueprints/
│   │   ├── customers/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   ├── mechanics/              # 🆕 New blueprint
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   └── service_tickets/        # 🆕 New blueprint
│   │       ├── __init__.py
│   │       ├── routes.py
│   │       └── schemas.py
│   ├── models/
│   │   └── ... (existing models)
│   └── extensions.py
├── collections/                    # 🆕 Postman collections
│   └── Mechanic_Shop_API.postman_collection.json
├── main.py
└── requirements.txt
```

---

## Step-by-Step Implementation Guide

### Step 1: Create the Mechanic Blueprint Structure

#### 1.1 Create the Folder
```bash
mkdir -p app/blueprints/mechanics
```

#### 1.2 Create `app/blueprints/mechanics/__init__.py`

This file initializes the blueprint and imports the routes so they're registered when the blueprint is loaded.

```python
from flask import Blueprint
from .routes import mechanic_bp

# Initialize the blueprint
def create_mechanic_blueprint():
    """Factory function to create and configure the mechanic blueprint."""
    return mechanic_bp

# For convenience, export the blueprint directly
__all__ = ['mechanic_bp']
```

**Why this matters:** The blueprint object is created in `routes.py`, then imported and exposed here. This keeps the blueprint initialization clean and follows Flask best practices.

#### 1.3 Create `app/blueprints/mechanics/schemas.py`

Define Marshmallow schemas for validation and serialization:

```python
from marshmallow import Schema, fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.mechanic import Mechanic

class MechanicSchema(SQLAlchemyAutoSchema):
    """
    Schema for serializing Mechanic objects and deserializing incoming JSON.
    Uses SQLAlchemyAutoSchema to automatically generate fields from the model.
    """
    
    class Meta:
        model = Mechanic
        load_instance = True  # Deserialize to model instances
        include_relationships = True  # Include related fields if needed
    
    # Define specific fields with validation
    name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=120),
        error_messages={
            'required': 'Mechanic name is required.',
            'null': 'Mechanic name cannot be null.'
        }
    )
    
    email = fields.Email(
        required=True,
        error_messages={'invalid': 'Invalid email format.'}
    )
    
    phone = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(min=1, max=15)
    )
    
    # Service tickets relationship (for GET responses)
    service_tickets = fields.Nested('ServiceTicketSchema', many=True, dump_only=True)


class MechanicUpdateSchema(Schema):
    """
    Schema for partial updates (PUT requests).
    All fields are optional to allow partial updates.
    """
    
    name = fields.String(
        required=False,
        validate=validate.Length(min=1, max=120)
    )
    
    email = fields.Email(required=False)
    phone = fields.String(required=False, allow_none=True)
```

**Key Concepts:**
- `SQLAlchemyAutoSchema`: Automatically creates fields matching your model
- `load_instance=True`: Marshmallow converts JSON to model instances
- `dump_only=True`: Fields that only appear in responses (not in request bodies)
- `required=True`: Enforces field presence in POST requests

#### 1.4 Create `app/blueprints/mechanics/routes.py`

Implement all CRUD endpoints:

```python
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.extensions import db
from app.models.mechanic import Mechanic
from .schemas import MechanicSchema, MechanicUpdateSchema

# Create the blueprint
mechanic_bp = Blueprint('mechanics', __name__, url_prefix='/mechanics')

# Initialize schemas
mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
mechanic_update_schema = MechanicUpdateSchema()

# ============================================================================
# CREATE: POST /mechanics/
# ============================================================================
@mechanic_bp.route('/', methods=['POST'])
def create_mechanic():
    """
    Create a new mechanic.
    
    Request body:
    {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "555-0123"
    }
    
    Returns:
        201: Created mechanic with id
        400: Validation error
    """
    try:
        # Validate and deserialize incoming JSON
        data = mechanic_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    # Create new mechanic instance
    new_mechanic = Mechanic(
        name=data['name'],
        email=data['email'],
        phone=data.get('phone')
    )
    
    # Add to database and commit
    db.session.add(new_mechanic)
    db.session.commit()
    
    # Return serialized mechanic with 201 Created status
    return jsonify(mechanic_schema.dump(new_mechanic)), 201


# ============================================================================
# READ: GET /mechanics/
# ============================================================================
@mechanic_bp.route('/', methods=['GET'])
def get_all_mechanics():
    """
    Retrieve all mechanics.
    
    Optional query parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 10)
    
    Returns:
        200: List of all mechanics
    """
    # Get pagination parameters from query string
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Fetch mechanics with pagination
    mechanics_paginated = db.paginate(
        db.select(Mechanic),
        page=page,
        per_page=per_page
    )
    
    # Serialize the mechanics
    return jsonify({
        'mechanics': mechanics_schema.dump(mechanics_paginated.items),
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': mechanics_paginated.total,
            'pages': mechanics_paginated.pages
        }
    }), 200


# ============================================================================
# UPDATE: PUT /mechanics/<int:id>
# ============================================================================
@mechanic_bp.route('/<int:id>', methods=['PUT'])
def update_mechanic(id):
    """
    Update a specific mechanic by ID.
    
    Request body (all fields optional):
    {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "555-9876"
    }
    
    Returns:
        200: Updated mechanic
        404: Mechanic not found
        400: Validation error
    """
    # Find mechanic by ID
    mechanic = db.session.get(Mechanic, id)
    if not mechanic:
        return jsonify({'error': 'Mechanic not found'}), 404
    
    try:
        # Validate incoming data (partial update)
        data = mechanic_update_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    # Update only provided fields
    if 'name' in data:
        mechanic.name = data['name']
    if 'email' in data:
        mechanic.email = data['email']
    if 'phone' in data:
        mechanic.phone = data['phone']
    
    # Commit changes
    db.session.commit()
    
    return jsonify(mechanic_schema.dump(mechanic)), 200


# ============================================================================
# DELETE: DELETE /mechanics/<int:id>
# ============================================================================
@mechanic_bp.route('/<int:id>', methods=['DELETE'])
def delete_mechanic(id):
    """
    Delete a specific mechanic by ID.
    
    Returns:
        204: Successfully deleted (no content)
        404: Mechanic not found
    """
    # Find mechanic by ID
    mechanic = db.session.get(Mechanic, id)
    if not mechanic:
        return jsonify({'error': 'Mechanic not found'}), 404
    
    # Delete and commit
    db.session.delete(mechanic)
    db.session.commit()
    
    return '', 204
```

**Pattern Explanation:**
1. **Validation First**: Use Marshmallow schemas to validate before creating/updating
2. **Try-Except for Errors**: Catch `ValidationError` and return 400 with details
3. **Query by ID**: Use `db.session.get()` for simple lookups
4. **Commit After Changes**: Always commit to persist database changes
5. **Return Serialized Data**: Use `schema.dump()` to convert model to JSON

---

### Step 2: Create the Service Ticket Blueprint

#### 2.1 Create the Folder
```bash
mkdir -p app/blueprints/service_tickets
```

#### 2.2 Create `app/blueprints/service_tickets/__init__.py`

```python
from flask import Blueprint
from .routes import service_ticket_bp

def create_service_ticket_blueprint():
    """Factory function to create and configure the service ticket blueprint."""
    return service_ticket_bp

__all__ = ['service_ticket_bp']
```

#### 2.3 Create `app/blueprints/service_tickets/schemas.py`

```python
from marshmallow import Schema, fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.service_ticket import ServiceTicket

class ServiceTicketSchema(SQLAlchemyAutoSchema):
    """
    Schema for serializing ServiceTicket objects.
    Includes nested mechanics and customer info.
    """
    
    class Meta:
        model = ServiceTicket
        load_instance = True
        include_relationships = True
    
    # Define fields with validation
    title = fields.String(
        required=True,
        validate=validate.Length(min=1, max=200),
        error_messages={'required': 'Service ticket title is required.'}
    )
    
    description = fields.String(required=False, allow_none=True)
    
    status = fields.String(
        required=True,
        validate=validate.OneOf(['open', 'in_progress', 'completed', 'on_hold']),
        error_messages={'invalid': 'Status must be: open, in_progress, completed, or on_hold.'}
    )
    
    customer_id = fields.Integer(required=True)
    
    # Nested fields for related objects (read-only)
    customer = fields.Nested('CustomerSchema', dump_only=True)
    mechanics = fields.Nested('MechanicSchema', many=True, dump_only=True)
    
    # Timestamps
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ServiceTicketCreateSchema(Schema):
    """Schema for creating new service tickets."""
    
    title = fields.String(
        required=True,
        validate=validate.Length(min=1, max=200)
    )
    
    description = fields.String(required=False, allow_none=True)
    
    status = fields.String(
        required=True,
        validate=validate.OneOf(['open', 'in_progress', 'completed', 'on_hold'])
    )
    
    customer_id = fields.Integer(required=True)


class ServiceTicketUpdateSchema(Schema):
    """Schema for updating service tickets."""
    
    title = fields.String(
        required=False,
        validate=validate.Length(min=1, max=200)
    )
    
    description = fields.String(required=False, allow_none=True)
    
    status = fields.String(
        required=False,
        validate=validate.OneOf(['open', 'in_progress', 'completed', 'on_hold'])
    )
```

#### 2.4 Create `app/blueprints/service_tickets/routes.py`

```python
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.extensions import db
from app.models.service_ticket import ServiceTicket
from app.models.mechanic import Mechanic
from .schemas import (
    ServiceTicketSchema,
    ServiceTicketCreateSchema,
    ServiceTicketUpdateSchema
)

# Create the blueprint
service_ticket_bp = Blueprint('service_tickets', __name__, url_prefix='/service-tickets')

# Initialize schemas
service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
create_schema = ServiceTicketCreateSchema()
update_schema = ServiceTicketUpdateSchema()

# ============================================================================
# CREATE: POST /service-tickets/
# ============================================================================
@service_ticket_bp.route('/', methods=['POST'])
def create_service_ticket():
    """
    Create a new service ticket.
    
    Request body:
    {
        "title": "Oil Change",
        "description": "Regular oil change service",
        "status": "open",
        "customer_id": 1
    }
    
    Returns:
        201: Created service ticket
        400: Validation error
        404: Customer not found
    """
    try:
        data = create_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    # Verify customer exists
    from app.models.customer import Customer
    customer = db.session.get(Customer, data['customer_id'])
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    # Create new service ticket
    new_ticket = ServiceTicket(
        title=data['title'],
        description=data.get('description'),
        status=data['status'],
        customer_id=data['customer_id']
    )
    
    db.session.add(new_ticket)
    db.session.commit()
    
    return jsonify(service_ticket_schema.dump(new_ticket)), 201


# ============================================================================
# READ: GET /service-tickets/
# ============================================================================
@service_ticket_bp.route('/', methods=['GET'])
def get_all_service_tickets():
    """
    Retrieve all service tickets.
    
    Optional query parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 10)
        status: Filter by status
        customer_id: Filter by customer ID
    
    Returns:
        200: List of service tickets with pagination info
    """
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    customer_id = request.args.get('customer_id', type=int)
    
    # Build query with filters
    query = db.select(ServiceTicket)
    
    if status:
        query = query.where(ServiceTicket.status == status)
    if customer_id:
        query = query.where(ServiceTicket.customer_id == customer_id)
    
    # Paginate
    tickets_paginated = db.paginate(query, page=page, per_page=per_page)
    
    return jsonify({
        'service_tickets': service_tickets_schema.dump(tickets_paginated.items),
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': tickets_paginated.total,
            'pages': tickets_paginated.pages
        }
    }), 200


# ============================================================================
# ASSIGN MECHANIC: PUT /service-tickets/<ticket_id>/assign-mechanic/<mechanic_id>
# ============================================================================
@service_ticket_bp.route('/<int:ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
def assign_mechanic(ticket_id, mechanic_id):
    """
    Assign a mechanic to a service ticket.
    
    Creates a many-to-many relationship between ServiceTicket and Mechanic.
    
    Returns:
        200: Updated service ticket with assigned mechanic
        404: Service ticket or mechanic not found
        409: Mechanic already assigned
    """
    # Find the ticket and mechanic
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({'error': 'Service ticket not found'}), 404
    
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({'error': 'Mechanic not found'}), 404
    
    # Check if mechanic is already assigned
    if mechanic in ticket.mechanics:
        return jsonify({'error': 'Mechanic already assigned to this ticket'}), 409
    
    # Append mechanic to the ticket's mechanics relationship
    ticket.mechanics.append(mechanic)
    db.session.commit()
    
    return jsonify(service_ticket_schema.dump(ticket)), 200


# ============================================================================
# REMOVE MECHANIC: PUT /service-tickets/<ticket_id>/remove-mechanic/<mechanic_id>
# ============================================================================
@service_ticket_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
def remove_mechanic(ticket_id, mechanic_id):
    """
    Remove a mechanic from a service ticket.
    
    Deletes the many-to-many relationship between ServiceTicket and Mechanic.
    
    Returns:
        200: Updated service ticket
        404: Service ticket or mechanic not found
        409: Mechanic not assigned to this ticket
    """
    # Find the ticket and mechanic
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({'error': 'Service ticket not found'}), 404
    
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({'error': 'Mechanic not found'}), 404
    
    # Check if mechanic is assigned to this ticket
    if mechanic not in ticket.mechanics:
        return jsonify({'error': 'Mechanic is not assigned to this ticket'}), 409
    
    # Remove mechanic from the ticket's mechanics relationship
    ticket.mechanics.remove(mechanic)
    db.session.commit()
    
    return jsonify(service_ticket_schema.dump(ticket)), 200
```

**Key Relationships:**
- `ticket.mechanics.append(mechanic)`: Adds mechanic to the many-to-many relationship
- `ticket.mechanics.remove(mechanic)`: Removes mechanic from the relationship
- These leverage Flask-SQLAlchemy's relationship attributes, which act like lists

---

### Step 3: Register Blueprints in Application Factory

Update `app/__init__.py` to register both new blueprints:

```python
from flask import Flask
from flask_cors import CORS
from app.extensions import db, jwt
from app.blueprints.customers import customer_bp
from app.blueprints.mechanics import mechanic_bp           # 🆕 Import
from app.blueprints.service_tickets import service_ticket_bp  # 🆕 Import

def create_app(config_name='development'):
    """Application Factory function."""
    
    app = Flask(__name__)
    
    # Load configuration
    if config_name == 'testing':
        from config import TestingConfig
        app.config.from_object(TestingConfig)
    else:
        from config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(customer_bp)           # Existing
    app.register_blueprint(mechanic_bp)           # 🆕 New
    app.register_blueprint(service_ticket_bp)    # 🆕 New
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app
```

**Important:** The `url_prefix` is already set in the blueprint definition, so you don't need to specify it again when registering.

---

## Testing with Postman

### Setting Up Postman Collections

#### Why Collections Matter?
Collections organize all your endpoints into logical groupings. This makes testing efficient and allows you to:
- Test all endpoints in sequence
- Share your API documentation with teammates
- Export and version control your tests
- Create environment variables for different servers

#### Creating a Collection

1. **Open Postman** and click **"Collections"** on the left sidebar
2. Click **"+ Create Collection"**
3. Name it: `Mechanic Shop API`
4. Click **"Create"**

#### Adding Requests to Your Collection

For each endpoint, create a new request:

1. Click **"+ Add request"** within your collection
2. Fill in the request details

### Sample Requests to Add

#### Mechanics Endpoints

**POST /mechanics - Create Mechanic**
```
Method: POST
URL: http://localhost:5000/mechanics/
Headers:
  Content-Type: application/json

Body (JSON):
{
  "name": "Alice Johnson",
  "email": "alice@shop.com",
  "phone": "555-0001"
}

Expected Response (201):
{
  "id": 1,
  "name": "Alice Johnson",
  "email": "alice@shop.com",
  "phone": "555-0001"
}
```

**GET /mechanics - List All Mechanics**
```
Method: GET
URL: http://localhost:5000/mechanics/?page=1&per_page=10
Headers: None needed

Expected Response (200):
{
  "mechanics": [
    {
      "id": 1,
      "name": "Alice Johnson",
      "email": "alice@shop.com",
      "phone": "555-0001"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 1,
    "pages": 1
  }
}
```

**PUT /mechanics/1 - Update Mechanic**
```
Method: PUT
URL: http://localhost:5000/mechanics/1
Headers:
  Content-Type: application/json

Body (JSON):
{
  "phone": "555-9999"
}

Expected Response (200): Updated mechanic object
```

**DELETE /mechanics/1 - Delete Mechanic**
```
Method: DELETE
URL: http://localhost:5000/mechanics/1
Headers: None

Expected Response (204): No content
```

#### Service Tickets Endpoints

**POST /service-tickets - Create Service Ticket**
```
Method: POST
URL: http://localhost:5000/service-tickets/
Headers:
  Content-Type: application/json

Body (JSON):
{
  "title": "Tire Replacement",
  "description": "Replace all four tires",
  "status": "open",
  "customer_id": 1
}

Expected Response (201):
{
  "id": 1,
  "title": "Tire Replacement",
  "description": "Replace all four tires",
  "status": "open",
  "customer_id": 1,
  "customer": { ... },
  "mechanics": [],
  "created_at": "2024-...",
  "updated_at": "2024-..."
}
```

**GET /service-tickets - List All Service Tickets**
```
Method: GET
URL: http://localhost:5000/service-tickets/?page=1&per_page=10
Headers: None

Query Parameters (optional):
  status: open
  customer_id: 1

Expected Response (200): List of service tickets with pagination
```

**PUT /service-tickets/1/assign-mechanic/1 - Assign Mechanic**
```
Method: PUT
URL: http://localhost:5000/service-tickets/1/assign-mechanic/1
Headers: None needed

Expected Response (200):
{
  "id": 1,
  "title": "Tire Replacement",
  "mechanics": [
    {
      "id": 1,
      "name": "Alice Johnson",
      "email": "alice@shop.com",
      "phone": "555-0001"
    }
  ]
}
```

**PUT /service-tickets/1/remove-mechanic/1 - Remove Mechanic**
```
Method: PUT
URL: http://localhost:5000/service-tickets/1/remove-mechanic/1
Headers: None

Expected Response (200): Service ticket with mechanic removed from list
```

### Exporting Your Collection

Once you've created and tested all requests:

1. Click the three dots (**⋯**) next to your collection name
2. Select **"Export"**
3. Choose **Collection v2.1** format
4. Click **"Export"**
5. Save as `Mechanic_Shop_API.postman_collection.json`
6. **Add this file to your project repository** under `collections/`

### Testing Strategy Checklist

- [ ] **Test happy paths first**: Valid data, expected 200/201/204 responses
- [ ] **Test error cases**: Missing required fields (expect 400)
- [ ] **Test not found**: Request non-existent IDs (expect 404)
- [ ] **Test relationships**: Assign and remove mechanics from tickets
- [ ] **Test pagination**: Verify `per_page` and `page` parameters work
- [ ] **Test filtering**: Use query parameters like `?status=open`
- [ ] **Test duplicates**: Try assigning same mechanic twice (expect 409)

---

## Common Issues & Troubleshooting

### Issue: "400 Validation Error - Invalid email format"
**Solution:** Check that your Mechanic model has an `email` field with appropriate constraints. Ensure you're sending a valid email format in Postman.

### Issue: "404 Mechanic not found"
**Solution:** Verify the mechanic ID exists before trying to update/delete. Use GET /mechanics/ to see all IDs first.

### Issue: "409 Mechanic already assigned"
**Solution:** The mechanic is already linked to that service ticket. This is by design to prevent duplicates. Remove first if reassigning.

### Issue: Changes not persisting in database
**Solution:** Make sure you're calling `db.session.commit()` after adding/updating/deleting. Without it, changes only exist in the session.

### Issue: Marshmallow schema validation errors
**Solution:** Review the exact error message in the response. Common issues:
- Missing required fields
- Email format invalid
- Status not in allowed values (`open`, `in_progress`, `completed`, `on_hold`)

---

## Summary Checklist

Before considering this phase complete, verify:

- [ ] **Mechanic Blueprint**
  - [ ] Folder structure created (`mechanics/__init__.py`, `routes.py`, `schemas.py`)
  - [ ] `MechanicSchema` and `MechanicUpdateSchema` defined
  - [ ] POST / (create) endpoint working
  - [ ] GET / (list all) endpoint working with pagination
  - [ ] PUT /<id> (update) endpoint working
  - [ ] DELETE /<id> (delete) endpoint working

- [ ] **Service Ticket Blueprint**
  - [ ] Folder structure created
  - [ ] `ServiceTicketSchema`, `ServiceTicketCreateSchema`, `ServiceTicketUpdateSchema` defined
  - [ ] POST / (create) endpoint working
  - [ ] GET / (list all) endpoint working with optional filters
  - [ ] PUT /<ticket_id>/assign-mechanic/<mechanic_id> working
  - [ ] PUT /<ticket_id>/remove-mechanic/<mechanic_id> working

- [ ] **Integration**
  - [ ] Both blueprints registered in `app/__init__.py`
  - [ ] Correct URL prefixes (`/mechanics`, `/service-tickets`)

- [ ] **Testing & Documentation**
  - [ ] Postman collection created with all endpoints
  - [ ] All endpoints tested and working
  - [ ] Collection exported as JSON
  - [ ] Collection saved to `collections/` folder in project
  - [ ] README completed and checked into version control

---

## Next Steps

After completing this phase:

1. **Test thoroughly**: Use the Postman collection to test edge cases and error scenarios
2. **Version control**: Commit your blueprints and updated `__init__.py`
3. **Document edge cases**: Note any special validation logic in code comments
4. **Prepare for integration**: Next phase will likely involve inventory and additional relationships
5. **Review code**: Look for opportunities to DRY up repeated patterns (error handling, pagination, etc.)

---

## Resources & References

- [Flask Blueprints Documentation](https://flask.palletsprojects.com/en/2.3.x/blueprints/)
- [Marshmallow Validation](https://marshmallow.readthedocs.io/en/stable/api_reference/)
- [Flask-SQLAlchemy Relationships](https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/models/#defining-models)
- [Postman Collections Guide](https://learning.postman.com/docs/sending-requests/intro-to-collections/)

---

## Questions to Consider

As you implement, think about:

1. **Why do we use separate schemas for create and update?** (Partial updates vs. full creation)
2. **What would happen if we deleted a mechanic who's assigned to a ticket?** (Foreign key constraints)
3. **How would we handle a service ticket with no mechanics assigned?** (Nullable relationships)
4. **Could we improve the assign/remove mechanic routes?** (Bulk operations? Error handling?)

Good luck! 🔧
