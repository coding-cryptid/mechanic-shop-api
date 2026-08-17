import pytest
import json
from datetime import datetime, timedelta


class TestServiceTicketsPost:
    # Tests for POST /service_tickets - Create service ticket
    
    def test_create_service_ticket_success(self, client, db, sample_customers):
        # Positive: Create ticket with valid data
        payload = {
            'customer_id': 1,
            'vin': 'ABC123456789',
            'service_date': '05/15/2024',
            'service_description': 'Oil change and filter replacement'
        }
        response = client.post('/service_tickets', json=payload)
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['customer_id'] == 1
        assert data['vin'] == 'ABC123456789'
        assert data['service_description'] == 'Oil change and filter replacement'
    
    def test_create_service_ticket_date_format_mmddyyyy(self, client, db, sample_customers):
        # Positive: Accept MM/DD/YYYY date format
        payload = {
            'customer_id': 1,
            'vin': 'ABC123456789',
            'service_date': '05/15/2024',
            'service_description': 'Oil change'
        }
        response = client.post('/service_tickets', json=payload)
        
        assert response.status_code == 201
    
    def test_create_service_ticket_date_format_mmddyy(self, client, db, sample_customers):
        # Positive: Accept MM/DD/YY date format
        payload = {
            'customer_id': 1,
            'vin': 'ABC123456789',
            'service_date': '05/15/24',
            'service_description': 'Oil change'
        }
        response = client.post('/service_tickets', json=payload)
        
        assert response.status_code == 201
    
    def test_create_service_ticket_date_format_yyyymmdd(self, client, db, sample_customers):
        # Positive: Accept YYYY-MM-DD date format
        payload = {
            'customer_id': 1,
            'vin': 'ABC123456789',
            'service_date': '2024-05-15',
            'service_description': 'Oil change'
        }
        response = client.post('/service_tickets', json=payload)
        
        assert response.status_code == 201
    
    def test_create_service_ticket_date_format_ddmmyyyy(self, client, db, sample_customers):
        # Positive: Accept DD/MM/YYYY date format
        payload = {
            'customer_id': 1,
            'vin': 'ABC123456789',
            'service_date': '15/05/2024',
            'service_description': 'Oil change'
        }
        response = client.post('/service_tickets', json=payload)
        
        assert response.status_code == 201
    
    def test_create_service_ticket_invalid_date_format(self, client, db, sample_customers):
        # Negative: Invalid date format
        payload = {
            'customer_id': 1,
            'vin': 'ABC123456789',
            'service_date': 'invalid-date',
            'service_description': 'Oil change'
        }
        response = client.post('/service_tickets', json=payload)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'date format' in data['message'].lower()
    
    def test_create_service_ticket_missing_customer_id(self, client, db):
        # Negative: Missing customer_id
        payload = {
            'vin': 'ABC123456789',
            'service_date': '05/15/2024',
            'service_description': 'Oil change'
        }
        response = client.post('/service_tickets', json=payload)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'customer_id' in data.get('fields', []) or 'missing' in data['message'].lower()
    
    def test_create_service_ticket_missing_vin(self, client, db, sample_customers):
        # Negative: Missing VIN
        payload = {
            'customer_id': 1,
            'service_date': '05/15/2024',
            'service_description': 'Oil change'
        }
        response = client.post('/service_tickets', json=payload)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'vin' in data.get('fields', []) or 'missing' in data['message'].lower()
    
    def test_create_service_ticket_missing_service_date(self, client, db, sample_customers):
        # Negative: Missing service_date
        payload = {
            'customer_id': 1,
            'vin': 'ABC123456789',
            'service_description': 'Oil change'
        }
        response = client.post('/service_tickets', json=payload)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'service_date' in data.get('fields', []) or 'missing' in data['message'].lower()
    
    def test_create_service_ticket_missing_description(self, client, db, sample_customers):
        # Negative: Missing service_description
        payload = {
            'customer_id': 1,
            'vin': 'ABC123456789',
            'service_date': '05/15/2024'
        }
        response = client.post('/service_tickets', json=payload)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'service_description' in data.get('fields', []) or 'missing' in data['message'].lower()
    
    def test_create_service_ticket_nonexistent_customer(self, client, db):
        # Negative: Customer ID doesn't exist
        payload = {
            'customer_id': 9999,
            'vin': 'ABC123456789',
            'service_date': '05/15/2024',
            'service_description': 'Oil change'
        }
        response = client.post('/service_tickets', json=payload)
 
        assert response.status_code in [400, 404, 500]
    
    def test_create_service_ticket_no_json(self, client, db):
        # Negative: No JSON payload
        response = client.post('/service_tickets')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'required' in data['message'].lower()
    
    def test_create_service_ticket_invalid_json(self, client, db):
        # Negative: Invalid JSON format
        response = client.post(
            '/service_tickets',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400


class TestServiceTicketsGetAll:
    # Tests for GET /service_tickets - Get all service tickets
    
    def test_get_all_service_tickets_success(self, client, db, sample_tickets):
        # Positive: Retrieve all service tickets
        response = client.get('/service_tickets')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_get_all_service_tickets_empty(self, client, db):
        # Positive: Get tickets when none exist
        response = client.get('/service_tickets')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_all_service_tickets_correct_fields(self, client, db, sample_tickets):
        # Positive: Returned tickets have correct fields
        response = client.get('/service_tickets')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        if len(data) > 0:
            ticket = data[0]
            assert 'id' in ticket
            assert 'customer_id' in ticket
            assert 'vin' in ticket
            assert 'service_date' in ticket
            assert 'service_description' in ticket
    
    def test_get_all_service_tickets_multiple(self, client, db, sample_customers):
        # Positive: Get multiple tickets
        for i in range(3):
            payload = {
                'customer_id': 1,
                'vin': f'VIN{i}',
                'service_date': '05/15/2024',
                'service_description': f'Service {i}'
            }
            client.post('/service_tickets', json=payload)
        
        response = client.get('/service_tickets')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 3


class TestServiceTicketsGetById:
    # Tests for GET /service_tickets/<id> - Get single service ticket
    
    def test_get_service_ticket_by_id_success(self, client, db, sample_tickets):
        # Positive: Retrieve existing ticket by ID
        response = client.get('/service_tickets/1')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == 1
    
    def test_get_service_ticket_nonexistent_id(self, client, db):
        # Negative: Retrieve non-existent ticket
        response = client.get('/service_tickets/9999')
        
        assert response.status_code in [404, 500]
    
    def test_get_service_ticket_invalid_id_format(self, client, db):
        # Negative: Invalid ID format (non-numeric)
        response = client.get('/service_tickets/abc')
        
        assert response.status_code == 404
    
    def test_get_service_ticket_negative_id(self, client, db):
        # Negative: Request with negative ID
        response = client.get('/service_tickets/-1')
        
        assert response.status_code in [404, 400]


class TestServiceTicketsPut:
    # Tests for PUT /service_tickets/<id> - Update service ticket
    
    def test_update_service_ticket_success(self, client, db, sample_tickets):
        # Positive: Update existing ticket
        payload = {
            'customer_id': 1,
            'vin': 'NEW123456789',
            'service_date': '06/15/2024',
            'service_description': 'Updated service description'
        }
        response = client.put('/service_tickets/1', json=payload)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['vin'] == 'NEW123456789'
        assert data['service_description'] == 'Updated service description'
    
    def test_update_service_ticket_nonexistent_id(self, client, db):
        # Negative: Update non-existent ticket
        payload = {
            'customer_id': 1,
            'vin': 'NEW123456789',
            'service_date': '06/15/2024',
            'service_description': 'Updated'
        }
        response = client.put('/service_tickets/9999', json=payload)
        
        assert response.status_code == 404
    
    def test_update_service_ticket_invalid_date(self, client, db, sample_tickets):
        # Negative: Update with invalid date format
        payload = {
            'customer_id': 1,
            'vin': 'NEW123456789',
            'service_date': 'invalid-date',
            'service_description': 'Updated'
        }
        response = client.put('/service_tickets/1', json=payload)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'date format' in data['message'].lower()
    
    def test_update_service_ticket_missing_customer_id(self, client, db, sample_tickets):
        # Negative: Update without customer_id
        payload = {
            'vin': 'NEW123456789',
            'service_date': '06/15/2024',
            'service_description': 'Updated'
        }
        response = client.put('/service_tickets/1', json=payload)
        
        assert response.status_code == 400
    
    def test_update_service_ticket_missing_vin(self, client, db, sample_tickets):
        # Negative: Update without VIN
        payload = {
            'customer_id': 1,
            'service_date': '06/15/2024',
            'service_description': 'Updated'
        }
        response = client.put('/service_tickets/1', json=payload)
        
        assert response.status_code == 400
    
    def test_update_service_ticket_missing_date(self, client, db, sample_tickets):
        # Negative: Update without service_date
        payload = {
            'customer_id': 1,
            'vin': 'NEW123456789',
            'service_description': 'Updated'
        }
        response = client.put('/service_tickets/1', json=payload)
        
        assert response.status_code == 400
    
    def test_update_service_ticket_missing_description(self, client, db, sample_tickets):
        # Negative: Update without service_description
        payload = {
            'customer_id': 1,
            'vin': 'NEW123456789',
            'service_date': '06/15/2024'
        }
        response = client.put('/service_tickets/1', json=payload)
        
        assert response.status_code == 400
    
    def test_update_service_ticket_no_json(self, client, db, sample_tickets):
        # Negative: Update with no JSON body
        response = client.put('/service_tickets/1')
        
        assert response.status_code == 400


class TestServiceTicketsEditMechanics:
    # Tests for PUT /service_tickets/<id>/edit - Bulk edit mechanics
    
    def test_edit_ticket_mechanics_add_success(self, client, db, sample_tickets, sample_mechanics):
        # Positive: Add mechanics to ticket
        payload = {
            'add_ids': [1, 2],
            'remove_ids': []
        }
        response = client.put('/service_tickets/1/edit', json=payload)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_edit_ticket_mechanics_remove_success(self, client, db, sample_tickets_with_mechanics):
        # Positive: Remove mechanics from ticket
        payload = {
            'add_ids': [],
            'remove_ids': [1]
        }
        response = client.put('/service_tickets/1/edit', json=payload)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_edit_ticket_mechanics_add_and_remove(self, client, db, sample_tickets_with_mechanics, sample_mechanics):
        # Positive: Add and remove mechanics in same request
        payload = {
            'add_ids': [2, 3],
            'remove_ids': [1]
        }
        response = client.put('/service_tickets/1/edit', json=payload)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_edit_ticket_mechanics_nonexistent_ticket(self, client, db):
        # Negative: Edit mechanics for non-existent ticket
        payload = {
            'add_ids': [1],
            'remove_ids': []
        }
        response = client.put('/service_tickets/9999/edit', json=payload)
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'not found' in data['message'].lower()
    
    def test_edit_ticket_mechanics_nonexistent_mechanic_add(self, client, db, sample_tickets):
        # Negative: Add non-existent mechanic
        payload = {
            'add_ids': [9999],
            'remove_ids': []
        }
        response = client.put('/service_tickets/1/edit', json=payload)
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'not found' in data['message'].lower()
    
    def test_edit_ticket_mechanics_nonexistent_mechanic_remove(self, client, db, sample_tickets):
        # Negative: Remove non-existent mechanic
        payload = {
            'add_ids': [],
            'remove_ids': [9999]
        }
        response = client.put('/service_tickets/1/edit', json=payload)
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'not found' in data['message'].lower()
    
    def test_edit_ticket_mechanics_invalid_add_ids_format(self, client, db, sample_tickets):
        # Negative: add_ids is not a list
        payload = {
            'add_ids': 'not_a_list',
            'remove_ids': []
        }
        response = client.put('/service_tickets/1/edit', json=payload)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'list' in data['message'].lower()
    
    def test_edit_ticket_mechanics_invalid_remove_ids_format(self, client, db, sample_tickets):
        # Negative: remove_ids is not a list
        payload = {
            'add_ids': [],
            'remove_ids': 'not_a_list'
        }
        response = client.put('/service_tickets/1/edit', json=payload)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'list' in data['message'].lower()
    
    def test_edit_ticket_mechanics_no_json(self, client, db, sample_tickets):
        # Negative: No JSON payload
        response = client.put('/service_tickets/1/edit')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'required' in data['message'].lower()
    
    def test_edit_ticket_mechanics_empty_lists(self, client, db, sample_tickets):
        # Positive: Empty add/remove lists (no-op)
        payload = {
            'add_ids': [],
            'remove_ids': []
        }
        response = client.put('/service_tickets/1/edit', json=payload)
        
        assert response.status_code == 200
    
    def test_edit_ticket_mechanics_duplicate_add_ids(self, client, db, sample_tickets, sample_mechanics):
        # Positive: Duplicate IDs in add_ids (should handle gracefully)
        payload = {
            'add_ids': [1, 1, 2],
            'remove_ids': []
        }
        response = client.put('/service_tickets/1/edit', json=payload)

        assert response.status_code in [200, 400]
    
    def test_edit_ticket_mechanics_add_same_mechanic_twice(self, client, db, sample_tickets_with_mechanics):
        # Positive: Try to add mechanic already on ticket (idempotent)
        payload = {
            'add_ids': [1],
            'remove_ids': []
        }
        response = client.put('/service_tickets/1/edit', json=payload)

        assert response.status_code == 200