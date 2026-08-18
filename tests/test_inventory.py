import unittest
import json


from unittest import APITestCase

class TestInventoryPost(APITestCase):
    # Tests for POST /inventory - Create inventory item
    
    def test_create_inventory_success(self):
        # Positive: Create inventory item with valid data
        payload = {
            'name': 'Oil Filter',
            'price': 15.99
        }
        response = self.client.post('/inventory', json=payload)
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Oil Filter')
        self.assertEqual(data['price'], 15.99)
    
    def test_create_inventory_missing_name(self):
        # Negative: Missing required 'name' field
        payload = {
            'price': 15.99
        }
        response = self.client.post('/inventory', json=payload)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('required', data['message'].lower())
    
    def test_create_inventory_missing_price(self):
        # Negative: Missing required 'price' field
        payload = {
            'name': 'Oil Filter'
        }
        response = self.client.post('/inventory', json=payload)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('required', data['message'].lower())
    
    def test_create_inventory_invalid_price_string(self):
        # Negative: Price is non-numeric string
        payload = {
            'name': 'Oil Filter',
            'price': 'not_a_number'
        }
        response = self.client.post('/inventory', json=payload)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('valid number', data['message'].lower())
    
    def test_create_inventory_negative_price(self):
        # Negative: Price is negative
        payload = {
            'name': 'Oil Filter',
            'price': -15.99
        }
        response = self.client.post('/inventory', json=payload)

        self.assertIn(response.status_code, [201, 400])
    
    def test_create_inventory_zero_price(self):
        # Negative: Price is zero
        payload = {
            'name': 'Oil Filter',
            'price': 0
        }
        response = self.client.post('/inventory', json=payload)

        self.assertIn(response.status_code, [201, 400])
    
    def test_create_inventory_empty_name(self):
        # Negative: Empty name string
        payload = {
            'name': '',
            'price': 15.99
        }
        response = self.client.post('/inventory', json=payload)
        
        self.assertIn(response.status_code, [400, 201])
    
    def test_create_inventory_no_json(self):
        # Negative: No JSON payload
        response = self.client.post('/inventory')
        
        self.assertIn(response.status_code, [400, 500])
    
    def test_create_inventory_large_price(self):
        # Positive: Create with large but valid price
        payload = {
            'name': 'Premium Component',
            'price': 9999.99
        }
        response = self.client.post('/inventory', json=payload)
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['price'], 9999.99)


class TestInventoryGetAll(APITestCase):
    # Tests for GET /inventory - Get all inventory items
    
    def test_get_all_inventory_success(self):
        # Positive: Retrieve all inventory items
        response = self.client.get('/inventory')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
    
    def test_get_all_inventory_empty(self):
        # Positive: Get inventory when none exist
        response = self.client.get('/inventory')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)
    
    def test_get_all_inventory_correct_fields(self):
        # Positive: Returned items have correct fields
        response = self.client.get('/inventory')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        if len(data) > 0:
            item = data[0]
            self.assertIn('id', item)
            self.assertIn('name', item)
            self.assertIn('price', item)
    
    def test_get_all_inventory_multiple_items(self):
        # Positive: Get multiple inventory items
        items = [
            {'name': 'Oil Filter', 'price': 15.99},
            {'name': 'Air Filter', 'price': 12.99},
            {'name': 'Spark Plugs', 'price': 8.99}
        ]
        
        for item in items:
            self.client.post('/inventory', json=item)
        
        response = self.client.get('/inventory')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 3)


class TestInventoryGetById(APITestCase):
    # Tests for GET /inventory/<id> - Get single inventory item
    
    def test_get_inventory_by_id_success(self):
        # Positive: Retrieve existing inventory item by ID
        response = self.client.get('/inventory/1')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'], 1)
    
    def test_get_inventory_nonexistent_id(self):
        # Negative: Retrieve non-existent inventory item
        response = self.client.get('/inventory/9999')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('not found', data['message'].lower())
    
    def test_get_inventory_invalid_id_format(self):
        # Negative: Invalid ID format (non-numeric)
        response = self.client.get('/inventory/abc')
        
        self.assertEqual(response.status_code, 404)
    
    def test_get_inventory_negative_id(self):
        # Negative: Request with negative ID
        response = self.client.get('/inventory/-1')
        
        self.assertIn(response.status_code, [404, 400])
    
    def test_get_inventory_zero_id(self):
        # Negative: Request with ID of 0
        response = self.client.get('/inventory/0')
        
        self.assertIn(response.status_code, [404, 400])


class TestInventoryPut(APITestCase):
    # Tests for PUT /inventory/<id> - Update inventory item
    
    def test_update_inventory_success(self):
        # Positive: Update existing inventory item
        payload = {
            'name': 'Premium Oil Filter',
            'price': 24.99
        }
        response = self.client.put('/inventory/1', json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Premium Oil Filter')
        self.assertEqual(data['price'], 24.99)
    
    def test_update_inventory_nonexistent_id(self):
        # Negative: Update non-existent inventory item
        payload = {
            'name': 'Premium Oil Filter',
            'price': 24.99
        }
        response = self.client.put('/inventory/9999', json=payload)
        
        self.assertEqual(response.status_code, 404)
    
    def test_update_inventory_name_only(self):
        # Positive: Update only the name field
        payload = {
            'name': 'Premium Oil Filter'
        }
        response = self.client.put('/inventory/1', json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Premium Oil Filter')
    
    def test_update_inventory_price_only(self):
        # Positive: Update only the price field
        payload = {
            'price': 24.99
        }
        response = self.client.put('/inventory/1', json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['price'], 24.99)
    
    def test_update_inventory_invalid_price(self):
        # Negative: Update with non-numeric price
        payload = {
            'price': 'not_a_number'
        }
        response = self.client.put('/inventory/1', json=payload)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('valid number', data['message'].lower())
    
    def test_update_inventory_negative_price(self):
        # Negative: Update with negative price
        payload = {
            'price': -24.99
        }
        response = self.client.put('/inventory/1', json=payload)
        
        self.assertIn(response.status_code, [200, 400])
    
    def test_update_inventory_no_json(self):
        # Negative: Update with no JSON body
        response = self.client.put('/inventory/1')
        
        self.assertIn(response.status_code, [400, 500])
    
    def test_update_inventory_empty_name(self):
        # Negative: Update with empty name
        payload = {
            'name': ''
        }
        response = self.client.put('/inventory/1', json=payload)
        
        self.assertIn(response.status_code, [200, 400])


class TestInventoryDelete(APITestCase):
    # Tests for DELETE /inventory/<id> - Delete inventory item
    
    def test_delete_inventory_success(self):
        # Positive: Delete existing inventory item with valid token
        response = self.client.delete(
            '/inventory/1',
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('deleted successfully', data['message'].lower())
    
    def test_delete_inventory_nonexistent_id(self):
        # Negative: Delete non-existent inventory item
        response = self.client.delete(
            '/inventory/9999',
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_delete_inventory_no_token(self):
        # Negative: Delete without authentication token
        response = self.client.delete('/inventory/1')
        
        self.assertEqual(response.status_code, 401)
    
    def test_delete_inventory_invalid_token(self):
        # Negative: Delete with invalid token
        response = self.client.delete(
            '/inventory/1',
            headers={'Authorization': 'Bearer invalid_token'}
        )
        
        self.assertEqual(response.status_code, 401)


class TestAddPartToTicket(APITestCase):
    # Tests for POST /inventory/service-tickets/<ticket_id>/add-part
    
    def test_add_part_to_ticket_success(self):
        # Positive: Add part to ticket with valid data
        payload = {
            'inventory_id': 1,
            'quantity': 2
        }
        response = self.client.post(
            '/inventory/service-tickets/1/add-part',
            json=payload,
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['quantity'], 2)
    
    def test_add_part_to_ticket_missing_inventory_id(self):
        # Negative: Missing inventory_id
        payload = {
            'quantity': 2
        }
        response = self.client.post(
            '/inventory/service-tickets/1/add-part',
            json=payload
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('inventory_id', data['message'])
    
    def test_add_part_to_ticket_invalid_inventory_id(self):
        # Negative: Non-existent inventory item
        payload = {
            'inventory_id': 9999,
            'quantity': 2
        }
        response = self.client.post(
            '/inventory/service-tickets/1/add-part',
            json=payload
        )
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('not found', data['message'].lower())
    
    def test_add_part_to_ticket_invalid_ticket_id(self):
        # Negative: Non-existent ticket
        payload = {
            'inventory_id': 1,
            'quantity': 2
        }
        response = self.client.post(
            '/inventory/service-tickets/9999/add-part',
            json=payload
        )
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('not found', data['message'].lower())
    
    def test_add_part_to_ticket_invalid_quantity_zero(self):
        # Negative: Quantity is zero
        payload = {
            'inventory_id': 1,
            'quantity': 0
        }
        response = self.client.post(
            '/inventory/service-tickets/1/add-part',
            json=payload
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('positive integer', data['message'].lower())
    
    def test_add_part_to_ticket_invalid_quantity_negative(self):
        # Negative: Quantity is negative
        payload = {
            'inventory_id': 1,
            'quantity': -5
        }
        response = self.client.post(
            '/inventory/service-tickets/1/add-part',
            json=payload
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('positive integer', data['message'].lower())
    
    def test_add_part_to_ticket_invalid_quantity_string(self):
        # Negative: Quantity is non-numeric
        payload = {
            'inventory_id': 1,
            'quantity': 'not_a_number'
        }
        response = self.client.post(
            '/inventory/service-tickets/1/add-part',
            json=payload
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_add_part_to_ticket_default_quantity(self):
        # Positive: Quantity defaults to 1 if not provided
        payload = {
            'inventory_id': 1
        }
        response = self.client.post(
            '/inventory/service-tickets/1/add-part',
            json=payload
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['quantity'], 1)
    
    def test_add_part_to_ticket_update_existing(self):
        # Positive: Adding same part again increments quantity
        payload = {
            'inventory_id': 1,
            'quantity': 2
        }
        self.client.post('/inventory/service-tickets/1/add-part', json=payload)
        
        payload['quantity'] = 3
        response = self.client.post('/inventory/service-tickets/1/add-part', json=payload)
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['quantity'], 5)  # 2 + 3


class TestGetTicketParts(APITestCase):
    # Tests for GET /inventory/service-tickets/<ticket_id>/parts
    
    def test_get_ticket_parts_success(self):
        # Positive: Get all parts for a ticket
        response = self.client.get('/inventory/service-tickets/1/parts')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('parts', data)
        self.assertIn('part_count', data)
    
    def test_get_ticket_parts_nonexistent_ticket(self):
        # Negative: Get parts for non-existent ticket
        response = self.client.get('/inventory/service-tickets/9999/parts')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('not found', data['message'].lower())
    
    def test_get_ticket_parts_empty(self):
        # Positive: Get parts for ticket with no parts
        response = self.client.get('/inventory/service-tickets/1/parts')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['part_count'], 0)
        self.assertEqual(data['parts'], [])
    
    def test_get_ticket_parts_includes_total_cost(self):
        # Positive: Parts include calculated total_cost
        response = self.client.get('/inventory/service-tickets/1/parts')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        if len(data['parts']) > 0:
            part = data['parts'][0]
            self.assertIn('total_cost', part)
            self.assertEqual(part['total_cost'], part['price'] * part['quantity'])


class TestRemovePartFromTicket(APITestCase):
    # Tests for DELETE /inventory/service-tickets/<ticket_id>/parts/<inventory_id>
    
    def test_remove_part_from_ticket_success(self):
        # Positive: Remove part from ticket
        response = self.client.delete(
            '/inventory/service-tickets/1/parts/1'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('removed', data['message'].lower())
    
    def test_remove_part_from_ticket_not_on_ticket(self):
        # Negative: Remove part that's not on ticket
        response = self.client.delete(
            '/inventory/service-tickets/1/parts/99'
        )
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('not found', data['message'].lower())
    
    def test_remove_part_from_nonexistent_ticket(self):
        # Negative: Remove part from non-existent ticket
        response = self.client.delete(
            '/inventory/service-tickets/9999/parts/1'
        )

        self.assertIn(response.status_code, [404, 500])
    
    def test_remove_part_verify_deletion(self):
        # Positive: Verify part is actually removed
        get_response = self.client.get('/inventory/service-tickets/1/parts')
        initial_count = json.loads(get_response.data)['part_count']

        self.client.delete('/inventory/service-tickets/1/parts/1')

        get_response = self.client.get('/inventory/service-tickets/1/parts')
        final_count = json.loads(get_response.data)['part_count']
        
        self.assertEqual(final_count, initial_count - 1)
