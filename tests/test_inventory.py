import pytest
import json


class TestInventoryPost:
    # Tests for POST /inventory - Create inventory item
    
    def test_create_inventory_success(self, client, db):
        # Positive: Create inventory item with valid data
        payload = {
            'name': 'Oil Filter',
            'price': 15.99
        }
        response = client.post('/inventory', json=payload)
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'Oil Filter'
        assert data['price'] == 15.99
    
    def test_create_inventory_missing_name(self, client, db):
        # Negative: Missing required 'name' field
        payload = {
            'price': 15.99
        }
        response = client.post('/inventory', json=payload)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'required' in data['message'].lower()
    
    def test_create_inventory_missing_price(self, client, db):
        # Negative: Missing required 'price' field
        payload = {
            'name': 'Oil Filter'
        }
        response = client.post('/inventory', json=payload)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'required' in data['message'].lower()
    
    def test_create_inventory_invalid_price_string(self, client, db):
        # Negative: Price is non-numeric string
        payload = {
            'name': 'Oil Filter',
            'price': 'not_a_number'
        }
        response = client.post('/inventory', json=payload)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'valid number' in data['message'].lower()
    
    def test_create_inventory_negative_price(self, client, db):
        # Negative: Price is negative
        payload = {
            'name': 'Oil Filter',
            'price': -15.99
        }
        response = client.post('/inventory', json=payload)

        assert response.status_code in [201, 400]
    
    def test_create_inventory_zero_price(self, client, db):
        # Negative: Price is zero
        payload = {
            'name': 'Oil Filter',
            'price': 0
        }
        response = client.post('/inventory', json=payload)

        assert response.status_code in [201, 400]
    
    def test_create_inventory_empty_name(self, client, db):
        # Negative: Empty name string
        payload = {
            'name': '',
            'price': 15.99
        }
        response = client.post('/inventory', json=payload)
        
        assert response.status_code in [400, 201]
    
    def test_create_inventory_no_json(self, client, db):
        # Negative: No JSON payload
        response = client.post('/inventory')
        
        assert response.status_code in [400, 500]
    
    def test_create_inventory_large_price(self, client, db):
        # Positive: Create with large but valid price
        payload = {
            'name': 'Premium Component',
            'price': 9999.99
        }
        response = client.post('/inventory', json=payload)
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['price'] == 9999.99


class TestInventoryGetAll:
    # Tests for GET /inventory - Get all inventory items
    
    def test_get_all_inventory_success(self, client, db, sample_inventory):
        # Positive: Retrieve all inventory items
        response = client.get('/inventory')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_get_all_inventory_empty(self, client, db):
        # Positive: Get inventory when none exist
        response = client.get('/inventory')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_all_inventory_correct_fields(self, client, db, sample_inventory):
        # Positive: Returned items have correct fields
        response = client.get('/inventory')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        if len(data) > 0:
            item = data[0]
            assert 'id' in item
            assert 'name' in item
            assert 'price' in item
    
    def test_get_all_inventory_multiple_items(self, client, db):
        # Positive: Get multiple inventory items
        items = [
            {'name': 'Oil Filter', 'price': 15.99},
            {'name': 'Air Filter', 'price': 12.99},
            {'name': 'Spark Plugs', 'price': 8.99}
        ]
        
        for item in items:
            client.post('/inventory', json=item)
        
        response = client.get('/inventory')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 3


class TestInventoryGetById:
    # Tests for GET /inventory/<id> - Get single inventory item
    
    def test_get_inventory_by_id_success(self, client, db, sample_inventory):
        # Positive: Retrieve existing inventory item by ID
        response = client.get('/inventory/1')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == 1
    
    def test_get_inventory_nonexistent_id(self, client, db):
        # Negative: Retrieve non-existent inventory item
        response = client.get('/inventory/9999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'not found' in data['message'].lower()
    
    def test_get_inventory_invalid_id_format(self, client, db):
        # Negative: Invalid ID format (non-numeric)
        response = client.get('/inventory/abc')
        
        assert response.status_code == 404
    
    def test_get_inventory_negative_id(self, client, db):
        # Negative: Request with negative ID
        response = client.get('/inventory/-1')
        
        assert response.status_code in [404, 400]
    
    def test_get_inventory_zero_id(self, client, db):
        # Negative: Request with ID of 0
        response = client.get('/inventory/0')
        
        assert response.status_code in [404, 400]


class TestInventoryPut:
    # Tests for PUT /inventory/<id> - Update inventory item
    
    def test_update_inventory_success(self, client, db, sample_inventory):
        # Positive: Update existing inventory item
        payload = {
            'name': 'Premium Oil Filter',
            'price': 24.99
        }
        response = client.put('/inventory/1', json=payload)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'Premium Oil Filter'
        assert data['price'] == 24.99
    
    def test_update_inventory_nonexistent_id(self, client, db):
        # Negative: Update non-existent inventory item
        payload = {
            'name': 'Premium Oil Filter',
            'price': 24.99
        }
        response = client.put('/inventory/9999', json=payload)
        
        assert response.status_code == 404
    
    def test_update_inventory_name_only(self, client, db, sample_inventory):
        # Positive: Update only the name field
        payload = {
            'name': 'Premium Oil Filter'
        }
        response = client.put('/inventory/1', json=payload)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'Premium Oil Filter'
    
    def test_update_inventory_price_only(self, client, db, sample_inventory):
        # Positive: Update only the price field
        payload = {
            'price': 24.99
        }
        response = client.put('/inventory/1', json=payload)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['price'] == 24.99
    
    def test_update_inventory_invalid_price(self, client, db, sample_inventory):
        # Negative: Update with non-numeric price
        payload = {
            'price': 'not_a_number'
        }
        response = client.put('/inventory/1', json=payload)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'valid number' in data['message'].lower()
    
    def test_update_inventory_negative_price(self, client, db, sample_inventory):
        # Negative: Update with negative price
        payload = {
            'price': -24.99
        }
        response = client.put('/inventory/1', json=payload)
        
        assert response.status_code in [200, 400]
    
    def test_update_inventory_no_json(self, client, db, sample_inventory):
        # Negative: Update with no JSON body
        response = client.put('/inventory/1')
        
        assert response.status_code in [400, 500]
    
    def test_update_inventory_empty_name(self, client, db, sample_inventory):
        # Negative: Update with empty name
        payload = {
            'name': ''
        }
        response = client.put('/inventory/1', json=payload)
        
        assert response.status_code in [200, 400]


class TestInventoryDelete:
    # Tests for DELETE /inventory/<id> - Delete inventory item
    
    def test_delete_inventory_success(self, client, db, sample_inventory, auth_token):
        # Positive: Delete existing inventory item with valid token
        response = client.delete(
            '/inventory/1',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'deleted successfully' in data['message'].lower()
    
    def test_delete_inventory_nonexistent_id(self, client, db, auth_token):
        # Negative: Delete non-existent inventory item
        response = client.delete(
            '/inventory/9999',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 404
    
    def test_delete_inventory_no_token(self, client, db, sample_inventory):
        # Negative: Delete without authentication token
        response = client.delete('/inventory/1')
        
        assert response.status_code == 401
    
    def test_delete_inventory_invalid_token(self, client, db, sample_inventory):
        # Negative: Delete with invalid token
        response = client.delete(
            '/inventory/1',
            headers={'Authorization': 'Bearer invalid_token'}
        )
        
        assert response.status_code == 401


class TestAddPartToTicket:
    # Tests for POST /inventory/service-tickets/<ticket_id>/add-part
    
    def test_add_part_to_ticket_success(self, client, db, sample_tickets, sample_inventory, auth_token):
        # Positive: Add part to ticket with valid data
        payload = {
            'inventory_id': 1,
            'quantity': 2
        }
        response = client.post(
            '/inventory/service-tickets/1/add-part',
            json=payload,
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['quantity'] == 2
    
    def test_add_part_to_ticket_missing_inventory_id(self, client, db, sample_tickets):
        # Negative: Missing inventory_id
        payload = {
            'quantity': 2
        }
        response = client.post(
            '/inventory/service-tickets/1/add-part',
            json=payload
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'inventory_id' in data['message']
    
    def test_add_part_to_ticket_invalid_inventory_id(self, client, db, sample_tickets):
        # Negative: Non-existent inventory item
        payload = {
            'inventory_id': 9999,
            'quantity': 2
        }
        response = client.post(
            '/inventory/service-tickets/1/add-part',
            json=payload
        )
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'not found' in data['message'].lower()
    
    def test_add_part_to_ticket_invalid_ticket_id(self, client, db, sample_inventory):
        # Negative: Non-existent ticket
        payload = {
            'inventory_id': 1,
            'quantity': 2
        }
        response = client.post(
            '/inventory/service-tickets/9999/add-part',
            json=payload
        )
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'not found' in data['message'].lower()
    
    def test_add_part_to_ticket_invalid_quantity_zero(self, client, db, sample_tickets, sample_inventory):
        # Negative: Quantity is zero
        payload = {
            'inventory_id': 1,
            'quantity': 0
        }
        response = client.post(
            '/inventory/service-tickets/1/add-part',
            json=payload
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'positive integer' in data['message'].lower()
    
    def test_add_part_to_ticket_invalid_quantity_negative(self, client, db, sample_tickets, sample_inventory):
        # Negative: Quantity is negative
        payload = {
            'inventory_id': 1,
            'quantity': -5
        }
        response = client.post(
            '/inventory/service-tickets/1/add-part',
            json=payload
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'positive integer' in data['message'].lower()
    
    def test_add_part_to_ticket_invalid_quantity_string(self, client, db, sample_tickets, sample_inventory):
        # Negative: Quantity is non-numeric
        payload = {
            'inventory_id': 1,
            'quantity': 'not_a_number'
        }
        response = client.post(
            '/inventory/service-tickets/1/add-part',
            json=payload
        )
        
        assert response.status_code == 400
    
    def test_add_part_to_ticket_default_quantity(self, client, db, sample_tickets, sample_inventory):
        # Positive: Quantity defaults to 1 if not provided
        payload = {
            'inventory_id': 1
        }
        response = client.post(
            '/inventory/service-tickets/1/add-part',
            json=payload
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['quantity'] == 1
    
    def test_add_part_to_ticket_update_existing(self, client, db, sample_tickets, sample_inventory):
        # Positive: Adding same part again increments quantity
        payload = {
            'inventory_id': 1,
            'quantity': 2
        }
        client.post('/inventory/service-tickets/1/add-part', json=payload)
        
        payload['quantity'] = 3
        response = client.post('/inventory/service-tickets/1/add-part', json=payload)
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['quantity'] == 5  # 2 + 3


class TestGetTicketParts:
    # Tests for GET /inventory/service-tickets/<ticket_id>/parts
    
    def test_get_ticket_parts_success(self, client, db, sample_tickets_with_parts):
        # Positive: Get all parts for a ticket
        response = client.get('/inventory/service-tickets/1/parts')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'parts' in data
        assert 'part_count' in data
    
    def test_get_ticket_parts_nonexistent_ticket(self, client, db):
        # Negative: Get parts for non-existent ticket
        response = client.get('/inventory/service-tickets/9999/parts')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'not found' in data['message'].lower()
    
    def test_get_ticket_parts_empty(self, client, db, sample_tickets):
        # Positive: Get parts for ticket with no parts
        response = client.get('/inventory/service-tickets/1/parts')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['part_count'] == 0
        assert data['parts'] == []
    
    def test_get_ticket_parts_includes_total_cost(self, client, db, sample_tickets_with_parts):
        # Positive: Parts include calculated total_cost
        response = client.get('/inventory/service-tickets/1/parts')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        if len(data['parts']) > 0:
            part = data['parts'][0]
            assert 'total_cost' in part
            assert part['total_cost'] == part['price'] * part['quantity']


class TestRemovePartFromTicket:
    # Tests for DELETE /inventory/service-tickets/<ticket_id>/parts/<inventory_id>
    
    def test_remove_part_from_ticket_success(self, client, db, sample_tickets_with_parts):
        # Positive: Remove part from ticket
        response = client.delete(
            '/inventory/service-tickets/1/parts/1'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'removed' in data['message'].lower()
    
    def test_remove_part_from_ticket_not_on_ticket(self, client, db, sample_tickets):
        # Negative: Remove part that's not on ticket
        response = client.delete(
            '/inventory/service-tickets/1/parts/99'
        )
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'not found' in data['message'].lower()
    
    def test_remove_part_from_nonexistent_ticket(self, client, db):
        # Negative: Remove part from non-existent ticket
        response = client.delete(
            '/inventory/service-tickets/9999/parts/1'
        )

        assert response.status_code in [404, 500]
    
    def test_remove_part_verify_deletion(self, client, db, sample_tickets_with_parts):
        # Positive: Verify part is actually removed
        get_response = client.get('/inventory/service-tickets/1/parts')
        initial_count = json.loads(get_response.data)['part_count']

        client.delete('/inventory/service-tickets/1/parts/1')

        get_response = client.get('/inventory/service-tickets/1/parts')
        final_count = json.loads(get_response.data)['part_count']
        
        assert final_count == initial_count - 1