# Mechanic Shop API

## Project Overview

The **Mechanic Shop API** is a full-featured REST API built with Flask and SQLAlchemy that manages operations for an automotive repair shop. It provides endpoints for managing customers, mechanics, service tickets, and inventory items, allowing the shop to streamline scheduling, track work orders, and organize staff assignments.

### Purpose

This API enables auto repair shops to:
- **Manage Customers**: Store and retrieve customer information, contact details, and service history
- **Track Mechanics**: Maintain a roster of mechanics and their certifications
- **Create Service Tickets**: Generate work orders that track vehicle repairs from creation to completion
- **Assign Work**: Connect multiple mechanics to service tickets for collaborative repairs
- **Manage Inventory**: Track parts and supplies used across jobs
- **Monitor Status**: Track the progress of jobs through different stages (open, in progress, completed, on hold)

### Key Features

- **RESTful API Architecture**: Standard HTTP methods (GET, POST, PUT, DELETE)
- **Role-Based Access Control**: JWT authentication and authorization (customer vs. admin roles)
- **Data Validation**: Marshmallow schemas validate all incoming data
- **Pagination & Filtering**: Browse large datasets with page-based results and filter by status, customer, etc.
- **Relationship Management**: Connect mechanics to tickets and track inventory across service jobs
- **Blueprint Organization**: Modular code structure with separate blueprints for each resource
- **Database Agnostic**: SQLAlchemy ORM allows easy switching between databases

---

## Project Structure

```
.
├── README.md
├── app
│   ├── __init__.py
│   ├── blueprints
│   │   ├── customers
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   ├── inventory
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   ├── mechanics
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   ├── service_tickets
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   └── users
│   │       ├── __init__.py
│   │       ├── routes.py
│   │       └── schemas.py
│   ├── extensions.py
│   ├── models.py
│   ├── static
│   │   └── swagger.yaml
│   └── utils
│       └── util.py
├── config.py
├── requirements.txt
├── run.py
└── venv

```

---

## Installation & Setup

### Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package manager)
- Git
- A code editor (VS Code recommended)
- Postman (for testing endpoints)

### Step 1: Clone or Download the Project

```bash
git clone <repository-url>
cd mechanic-shop-api
```

### Step 2: Create a Virtual Environment

Virtual environments isolate project dependencies and prevent conflicts with other Python projects.

```bash
python -m venv venv
```

Activate the virtual environment:

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

You should see `(venv)` at the beginning of your terminal prompt.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs all required packages including:
- Flask (web framework)
- Flask-SQLAlchemy (database ORM)
- Flask-JWT-Extended (authentication)
- Marshmallow (data validation)
- SQLAlchemy (database toolkit)
- Python-JOSE (JWT tokens)
- Flask-CORS (cross-origin requests)

### Step 4: Configure the Database

By default, the API uses SQLite for development. The database file is created automatically when you first run the app.

If you need to use a different database (PostgreSQL, MySQL), update the `SQLALCHEMY_DATABASE_URI` in `config.py`:

```
SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost/mechanic_shop'
```

### Step 5: Run the Application

```bash
python main.py
```

The API will start on `http://localhost:5000`

You should see output similar to:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

---

## Using the API

### Base URL

```
http://localhost:5000
```

### Authentication

The API uses JWT (JSON Web Tokens) for authentication. To access protected endpoints:

1. Register a new user (if signup endpoint is available)
2. Login to receive a JWT token
3. Include the token in the `Authorization` header for all requests:

```
Authorization: Bearer <your_jwt_token>
```

### API Endpoints Overview

#### Customers (`/customers`)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/customers/` | Create a new customer |
| GET | `/customers/` | List all customers (with pagination) |
| PUT | `/customers/<id>` | Update a customer |
| DELETE | `/customers/<id>` | Delete a customer |

#### Mechanics (`/mechanics`)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/mechanics/` | Create a new mechanic |
| GET | `/mechanics/` | List all mechanics |
| PUT | `/mechanics/<id>` | Update a mechanic |
| DELETE | `/mechanics/<id>` | Delete a mechanic |

#### Service Tickets (`/service-tickets`)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/service-tickets/` | Create a new service ticket |
| GET | `/service-tickets/` | List all tickets (filterable by status, customer) |
| PUT | `/service-tickets/<id>/edit/` | Assign and/or remove mechanic to a ticket |

### Example API Usage

#### 1. Create a Customer

**Request:**
```
POST http://localhost:5000/customers/
Content-Type: application/json

{
  "name": "John Smith",
  "email": "john@example.com",
  "phone_number": "555-0123"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "John Smith",
  "email": "john@example.com",
  "phone_number": "555-0123"
}
```

#### 2. Create a Service Ticket

**Request:**
```
POST http://localhost:5000/service-tickets/
Content-Type: application/json

{
  "description": "Regular oil change and filter replacement",
  "customer_id": 1,
  "service_date": "2026-01-14",
  "vin": SHSUF16253A
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "description": "Regular oil change and filter replacement",
  "customer_id": 1,
  "service_date": "2026-01-14",
  "vin": SHSUF16253A
}
```

#### 3. Assign a Mechanic to a Ticket

**Request:**
```
PUT http://localhost:5000/service-tickets/1/assign-mechanic/1
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Oil Change",
  "status": "open",
  "mechanics": [
    {
      "id": 1,
      "name": "Alice Johnson",
      "email": "alice@shop.com"
    }
  ]
}
```

#### 4. List All Service Tickets with Filters

**Request:**
```
GET http://localhost:5000/service-tickets/
```

**Response (200 OK):**
```json
  "service_tickets": [
    {
      "id": 1,
      "title": "Oil Change",
      "status": "open",
      "customer_id": 1
    }
  ]
```
## Rate Limiting & Caching
 
The API implements performance optimizations to ensure fair usage and fast response times.
 
### Rate Limiting
 
**What it is:** Rate limiting prevents any single user or client from making too many requests in a short period, protecting the server from being overwhelmed.
 
**How it works:**
- Each endpoint has a request limit (e.g., "100 requests per hour")
- When you exceed the limit, you'll receive a **429 Too Many Requests** error
- The response includes headers telling you when the limit resets
**Example response when rate limited:**
```
HTTP/1.1 429 Too Many Requests
Retry-After: 3600
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1610000000
```
 
**Tips to avoid hitting limits:**
- Cache responses in your client application when possible
- Batch multiple operations when feasible
- Implement exponential backoff in your retry logic
- Use pagination to fetch large datasets in smaller chunks
### Response Caching
 
**What it is:** Caching stores frequently-accessed data in memory, so repeated requests return instantly without hitting the database.
 
**Which endpoints are cached:**
- List endpoints (GET `/customers/`, GET `/mechanics/`, etc.) are cached for faster browsing
- Cached responses are automatically invalidated when data is updated
**How caching helps you:**
- Faster response times for browsing data
- Reduced server load
- Better user experience
**Cache behavior:**
- Cached data is typically refreshed every 5-15 minutes (depending on endpoint)
- Creating, updating, or deleting resources clears related caches immediately
- No action needed on your part—caching is transparent
---
 
## Advanced Queries
 
The API includes powerful query capabilities for complex workflows.
 
### Mechanic Ranking by Workload
 
Find out which mechanics have worked on the most service tickets.
 
**Request:**
```
GET http://localhost:5000/mechanics/ranking
```
 
**Response (200 OK):**
```json
{
  "mechanics": [
    {
      "id": 2,
      "name": "Bob Martinez",
      "email": "bob@shop.com",
      "tickets_worked": 15
    },
    {
      "id": 1,
      "name": "Alice Johnson",
      "email": "alice@shop.com",
      "tickets_worked": 12
    }
  ]
}
```
 
**Use cases:**
- Identify top performers
- Balance workload among team members
- Understand skill utilization
### Pagination for Large Datasets
 
When listing customers, mechanics, or service tickets, the API returns paginated results to improve performance.
 
**Query parameters:**
- `page`: Which page to retrieve (default: 1)
- `per_page`: How many items per page (default: 10, max: 100)
**Example:**
```
GET http://localhost:5000/customers/?page=2&per_page=20
```
 
**Response includes pagination metadata:**
```json
{
  "customers": [...],
  "pagination": {
    "page": 2,
    "per_page": 20,
    "total": 150,
    "pages": 8
  }
}
---

## Testing with Postman

### Import the Postman Collection

A Postman collection is provided with pre-configured requests for all endpoints.

1. **Open Postman**
2. Click **"Import"** in the top-left
3. Choose **"Upload Files"**
4. Select `collections/Mechanic_Shop_API.postman_collection.json`
5. Click **"Import"**

All endpoints will now be available in the Postman sidebar, organized by resource.

### Running Tests

1. **Select an endpoint** from the collection
2. **Update variables** as needed (e.g., customer ID, mechanic ID)
3. Click **"Send"**
4. Review the response in the **Body** tab

### Quick Test Workflow

Follow this order to test the full workflow:

1. **Create a Customer** → Copy the returned `id`
2. **Create a Mechanic** → Copy the returned `id`
3. **Create a Service Ticket** → Use the customer `id` from step 1
4. **Assign a Mechanic** → Use the service ticket `id` and mechanic `id`
5. **List Service Tickets** → Verify the mechanic is assigned
6. **Remove a Mechanic** → Use the same endpoint parameters
7. **Update/Delete** → Test the remaining endpoints

### Common Postman Features

**Environment Variables:**
Set up variables for dynamic testing (e.g., `{{base_url}}`, `{{customer_id}}`):
1. Click the **gear icon** → **Environments**
2. Create a new environment
3. Add variables and their values

---

## HTTP Status Codes

The API uses standard HTTP status codes:

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | Successful GET, PUT, or DELETE |
| 201 | Created | Successful POST (new resource created) |
| 204 | No Content | Successful DELETE (no response body) |
| 400 | Bad Request | Validation error or missing required fields |
| 401 | Unauthorized | Missing or invalid JWT token |
| 403 | Forbidden | User lacks permission (role-based access) |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Logic error (e.g., mechanic already assigned) |
| 500 | Server Error | Unexpected server issue |

---

## Common Workflows

### Workflow 1: Create a Service Ticket and Assign Multiple Mechanics

1. Create a customer (or use existing customer ID)
2. Create a service ticket with that customer ID
3. Create mechanics (or use existing mechanic IDs)
4. Assign each mechanic to the ticket individually using the assign endpoint
5. View the ticket to confirm all mechanics are assigned

### Workflow 2: Track Ticket Progress

1. Create a service ticket with status `"open"`
2. Update the ticket status to `"in_progress"` when work starts
3. Assign mechanics as they join the job
4. Update the status to `"completed"` when finished
5. Archive or close the ticket

### Workflow 3: Filter Tickets by Status

1. Use GET `/service-tickets/?status=open` to see open work
2. Use GET `/service-tickets/?status=in_progress` to see active jobs
3. Use GET `/service-tickets/?status=completed` to see finished jobs
4. Combine filters: `?status=open&customer_id=5` to find a specific customer's pending work

---

## Troubleshooting

### Issue: "Connection refused" when starting the server
**Solution:** Make sure the Flask app is properly configured and all dependencies are installed. Run `pip install -r requirements.txt` again.

### Issue: "400 Bad Request" when creating a resource
**Solution:** Check that all required fields are included in the request body and that they have valid values (correct email format, status values, etc.).

### Issue: "404 Not Found" when accessing an endpoint
**Solution:** Verify the resource ID exists. Use a GET request to list all resources and confirm the ID.

### Issue: "409 Conflict" when assigning a mechanic
**Solution:** The mechanic is already assigned to that ticket. Use the remove endpoint first if you need to reassign.

### Issue: Database errors when starting the app
**Solution:** Delete the database file (usually `instance/database.db`) and restart the app. This will recreate the database with the current schema.

### Issue: "CORS error" when calling from frontend
**Solution:** The API has CORS enabled by default. If issues persist, check that requests include the proper `Content-Type` headers.

---

## Environment Variables

Create a `.env` file in the project root for sensitive configuration:

```
FLASK_ENV=development
FLASK_APP=main.py
JWT_SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///instance/mechanic_shop.db
```

Never commit `.env` to version control. Add it to `.gitignore`.

---

## Development Tips

### Enable Debug Mode
Debug mode provides better error messages and auto-reloads when files change:

```bash
export FLASK_ENV=development
python main.py
```

### Database Migrations
If you modify models, you may need to recreate the database or use a migration tool like Alembic.

### Logging
Add logging to `main.py` to monitor API activity:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### API Documentation
Consider using Swagger/OpenAPI to auto-generate interactive API documentation that appears at `/api/docs`.

---

## Next Steps

After setting up and testing the API:

1. **Customize Models**: Adjust data models to match your shop's specific needs
2. **Add More Endpoints**: Extend with inventory tracking, invoicing, or reporting
3. **Deploy**: Move from development to production using Heroku, AWS, DigitalOcean, etc.
4. **Frontend Integration**: Build a web or mobile interface to consume the API
5. **Testing**: Write unit tests and integration tests for all endpoints

---

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/)
- [Marshmallow Validation](https://marshmallow.readthedocs.io/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc7519)
- [RESTful API Design Guide](https://restfulapi.net/)
- [Postman Learning Center](https://learning.postman.com/)

---

## Support & Questions

If you encounter issues or have questions:

1. Check the **Troubleshooting** section above
2. Review endpoint documentation in the Postman collection
3. Check Flask and SQLAlchemy documentation
4. Review error messages in the server logs (terminal output)

Good luck building with the Mechanic Shop API! 🔧
