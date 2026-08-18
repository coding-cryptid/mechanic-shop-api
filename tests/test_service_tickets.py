import unittest
import json
from datetime import datetime, timedelta


from test_base import APITestCase

class TestServiceTicketsPost(APITestCase):
    # Tests for POST /service_tickets - Create service ticket
    
    def test_create_service_ticket_success(self):
        # Positive: Create ticket with valid data
        payload = {
            'customer_id': 1,
            'vin': 'ABC123456789',
            'service_date': '05/15/2024',
            'service_description': 'Oil change and filter replacement'
        }
        response = self.client.post('/service_tickets', json=payload)
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['customer_id'], 1)
        self.assertEqual(data['vin'], 'ABC123456789')
        self.assertEqual(data['service_description'], 'Oil change and filter replacement')
    
    def test_create_service_ticket_date_format_mmddyyyy(self):
        # Positive: Accept MM/DD/YYYY date format
        payload = {
            'customer_id': 1,
            'vin': 'ABC123456789',
            'service_date': '05/15/2024',
            'service_description': 'Oil change'
        }
        response = self.client.post('/service_tickets', json=payload)
        
        self.assertEqual(response.status_code, 201)
    
    def test_create_service_ticket_date_format_mmddyy(self):
        # Positive: Accept MM/DD/YY date format
        payload = {
            'customer_id': 1,
            'vin': 'ABC123456789',
            'service_date': '05/15/24',
            'service_description': 'Oil change'
        }
        response = self.client.post('/service_tickets', json=payload)
        
        self.assertEqual(response.status_code, 201)
    
    def test_create_service_ticket_date_format_yyyymmdd(self):
        # Positive: Accept YYYY-MM-DD date format
        payload = {
            'customer_id': 1,
            'vin': 'ABC123456789',
            'service_date': '2024-05-15',
            'service_description': 'Oil change'
        }
        response = self.client.post('/service_tickets', json=payload)
        
        self.assertEqual(response.status_code, 201)
    
    def test_create_service_ticket_date_format_ddmmyyyy(self):
        # Positive: Accept DD/MM/YYYY date format
        payload = {
            'customer_id': 1,
            'vin': 'ABC123456789',
            'service_date': '15/05/2024',
            'service_description': 'Oil change'
        }
        response = self.client.post('/service_tickets', json=payload)
        
        self.assertEqual(response.status_code, 201)
    
    def test_create_service_ticket_invalid_date_format(self):
        # Negative: Invalid date format
        payload = {
            'customer_id': 1,
            'vin': 'ABC123456789',
            'service_date': 'invalid-date',
            'service_description': 'Oil change'
        }
        response = self.client.post('/service_tickets', json=payload)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('date format', data['message'].lower())
    
    def test_create_service_ticket_missing_customer_id(self):
        # Negative: Missing customer_id
        payload = {
            'vin': 'ABC123456789',
            'service_date': '05/15/2024',
            'service_description': 'Oil change'
        }
        response = self.client.post('/service_tickets', json=payload)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertTrue(
            'customer_id' in data.get('fields', []) or
            'missing' in data['message'].lower()
        )
    
    def test_create_service_ticket_missing_vin(self):
        # Negative: Missing VIN
        payload = {
            'customer_id': 1,
            'service_date': '05/15/2024',
            'service_description': 'Oil change'
        }
        response = self.client.post('/service_tickets', json=payload)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertTrue(
            'vin' in data.get('fields', []) or
            'missing' in data['message'].lower()
        )
    
    def test_create_service_ticket_missing_service_date(self):
        # Negative: Missing service_date
        payload = {
            'customer_id': 1,
            'vin': 'ABC123456789',
            'service_description': 'Oil change'
        }
        response = self.client.post('/service_tickets', json=payload)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertTrue(
            'service_date' in data.get('fields', []) or
            'missing' in data['message'].lower()
        )
    
    def test_create_service_ticket_missing_description(self):
        # Negative: Missing service_description
        payload = {
            'customer_id': 1,
            'vin': 'ABC123456789',
            'service_date': '05/15/2024'
        }
        response = self.client.post('/service_tickets', json=payload)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertTrue(
            'service_description' in data.get('fields', []) or
            'missing' in data['message'].lower()
        )
    
    def test_create_service_ticket_nonexistent_customer(self):
        # Negative: Customer ID doesn't exist
        payload = {
            'customer_id': 9999,
            'vin': 'ABC123456789',
            'service_date': '05/15/2024',
            'service_description': 'Oil change'
        }
        response = self.client.post('/service_tickets', json=payload)
 
        self.assertIn(response.status_code, [400, 404, 500])
    
    def test_create_service_ticket_no_json(self):
        # Negative: No JSON payload
        response = self.client.post('/service_tickets')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('required', data['message'].lower())
    
    def test_create_service_ticket_invalid_json(self):
        # Negative: Invalid JSON format
        response = self.client.post(
            '/service_tickets',
            data='invalid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)


class TestServiceTicketsGetAll(APITestCase):
    # Tests for GET /service_tickets - Get all service tickets
    
    def test_get_all_service_tickets_success(self):
        # Positive: Retrieve all service tickets
        response = self.client.get('/service_tickets')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
    
    def test_get_all_service_tickets_empty(self):
        # Positive: Get tickets when none exist
        response = self.client.get('/service_tickets')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)
    
    def test_get_all_service_tickets_correct_fields(self):
        # Positive: Returned tickets have correct fields
        response = self.client.get('/service_tickets')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        if len(data) > 0:
            ticket = data[0]
            self.assertIn('id', ticket)
            self.assertIn('customer_id', ticket)
            self.assertIn('vin', ticket)
            self.assertIn('service_date', ticket)
            self.assertIn('service_description', ticket)
    
    def test_get_all_service_tickets_multiple(self):
        # Positive: Get multiple tickets
        for i in range(3):
            payload = {
                'customer_id': 1,
                'vin': f'VIN{i}',
                'service_date': '05/15/2024',
                'service_description': f'Service {i}'
            }
            self.client.post('/service_tickets', json=payload)
        
        response = self.client.get('/service_tickets')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 3)


class TestServiceTicketsGetById(APITestCase):
    # Tests for GET /service_tickets/<id> - Get single service ticket
    
    def test_get_service_ticket_by_id_success(self):
        # Positive: Retrieve existing ticket by ID
        response = self.client.get('/service_tickets/1')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'], 1)
    
    def test_get_service_ticket_nonexistent_id(self):
        # Negative: Retrieve non-existent ticket
        response = self.client.get('/service_tickets/9999')
        
        self.assertIn(response.status_code, [404, 500])
    
    def test_get_service_ticket_invalid_id_format(self):
        # Negative: Invalid ID format (non-numeric)
        response = self.client.get('/service_tickets/abc')
        
        self.assertEqual(response.status_code, 404)
    
    def test_get_service_ticket_negative_id(self):
        # Negative: Request with negative ID
        response = self.client.get('/service_tickets/-1')
        
        self.assertIn(response.status_code, [404, 400])


class TestServiceTicketsPut(APITestCase):
    # Tests for PUT /service_tickets/<id> - Update service ticket
    
    def test_update_service_ticket_success(self):
        # Positive: Update existing ticket
        payload = {
            'customer_id': 1,
            'vin': 'NEW123456789',
            'service_date': '06/15/2024',
            'service_description': 'Updated service description'
        }
        response = self.client.put('/service_tickets/1', json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['vin'], 'NEW123456789')
        self.assertEqual(data['service_description'], 'Updated service description')
    
    def test_update_service_ticket_nonexistent_id(self):
        # Negative: Update non-existent ticket
        payload = {
            'customer_id': 1,
            'vin': 'NEW123456789',
            'service_date': '06/15/2024',
            'service_description': 'Updated'
        }
        response = self.client.put('/service_tickets/9999', json=payload)
        
        self.assertEqual(response.status_code, 404)
    
    def test_update_service_ticket_invalid_date(self):
        # Negative: Update with invalid date format
        payload = {
            'customer_id': 1,
            'vin': 'NEW123456789',
            'service_date': 'invalid-date',
            'service_description': 'Updated'
        }
        response = self.client.put('/service_tickets/1', json=payload)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('date format', data['message'].lower())
    
    def test_update_service_ticket_missing_customer_id(self):
        # Negative: Update without customer_id
        payload = {
            'vin': 'NEW123456789',
            'service_date': '06/15/2024',
            'service_description': 'Updated'
        }
        response = self.client.put('/service_tickets/1', json=payload)
        
        self.assertEqual(response.status_code, 400)
    
    def test_update_service_ticket_missing_vin(self):
        # Negative: Update without VIN
        payload = {
            'customer_id': 1,
            'service_date': '06/15/2024',
            'service_description': 'Updated'
        }
        response = self.client.put('/service_tickets/1', json=payload)
        
        self.assertEqual(response.status_code, 400)
    
    def test_update_service_ticket_missing_date(self):
        # Negative: Update without service_date
        payload = {
            'customer_id': 1,
            'vin': 'NEW123456789',
            'service_description': 'Updated'
        }
        response = self.client.put('/service_tickets/1', json=payload)
        
        self.assertEqual(response.status_code, 400)
    
    def test_update_service_ticket_missing_description(self):
        # Negative: Update without service_description
        payload = {
            'customer_id': 1,
            'vin': 'NEW123456789',
            'service_date': '06/15/2024'
        }
        response = self.client.put('/service_tickets/1', json=payload)
        
        self.assertEqual(response.status_code, 400)
    
    def test_update_service_ticket_no_json(self):
        # Negative: Update with no JSON body
        response = self.client.put('/service_tickets/1')
        
        self.assertEqual(response.status_code, 400)


class TestServiceTicketsEditMechanics(APITestCase):
    # Tests for PUT /service_tickets/<id>/edit - Bulk edit mechanics
    
    def test_edit_ticket_mechanics_add_success(self):
        # Positive: Add mechanics to ticket
        payload = {
            'add_ids': [1, 2],
            'remove_ids': []
        }
        response = self.client.put('/service_tickets/1/edit', json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
    
    def test_edit_ticket_mechanics_remove_success(self):
        # Positive: Remove mechanics from ticket
        payload = {
            'add_ids': [],
            'remove_ids': [1]
        }
        response = self.client.put('/service_tickets/1/edit', json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
    
    def test_edit_ticket_mechanics_add_and_remove(self):
        # Positive: Add and remove mechanics in same request
        payload = {
            'add_ids': [2, 3],
            'remove_ids': [1]
        }
        response = self.client.put('/service_tickets/1/edit', json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
    
    def test_edit_ticket_mechanics_nonexistent_ticket(self):
        # Negative: Edit mechanics for non-existent ticket
        payload = {
            'add_ids': [1],
            'remove_ids': []
        }
        response = self.client.put('/service_tickets/9999/edit', json=payload)
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('not found', data['message'].lower())
    
    def test_edit_ticket_mechanics_nonexistent_mechanic_add(self):
        # Negative: Add non-existent mechanic
        payload = {
            'add_ids': [9999],
            'remove_ids': []
        }
        response = self.client.put('/service_tickets/1/edit', json=payload)
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('not found', data['message'].lower())
    
    def test_edit_ticket_mechanics_nonexistent_mechanic_remove(self):
        # Negative: Remove non-existent mechanic
        payload = {
            'add_ids': [],
            'remove_ids': [9999]
        }
        response = self.client.put('/service_tickets/1/edit', json=payload)
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('not found', data['message'].lower())
    
    def test_edit_ticket_mechanics_invalid_add_ids_format(self):
        # Negative: add_ids is not a list
        payload = {
            'add_ids': 'not_a_list',
            'remove_ids': []
        }
        response = self.client.put('/service_tickets/1/edit', json=payload)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('list', data['message'].lower())
    
    def test_edit_ticket_mechanics_invalid_remove_ids_format(self):
        # Negative: remove_ids is not a list
        payload = {
            'add_ids': [],
            'remove_ids': 'not_a_list'
        }
        response = self.client.put('/service_tickets/1/edit', json=payload)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('list', data['message'].lower())
    
    def test_edit_ticket_mechanics_no_json(self):
        # Negative: No JSON payload
        response = self.client.put('/service_tickets/1/edit')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('required', data['message'].lower())
    
    def test_edit_ticket_mechanics_empty_lists(self):
        # Positive: Empty add/remove lists (no-op)
        payload = {
            'add_ids': [],
            'remove_ids': []
        }
        response = self.client.put('/service_tickets/1/edit', json=payload)
        
        self.assertEqual(response.status_code, 200)
    
    def test_edit_ticket_mechanics_duplicate_add_ids(self):
        # Positive: Duplicate IDs in add_ids (should handle gracefully)
        payload = {
            'add_ids': [1, 1, 2],
            'remove_ids': []
        }
        response = self.client.put('/service_tickets/1/edit', json=payload)

        self.assertIn(response.status_code, [200, 400])
    
    def test_edit_ticket_mechanics_add_same_mechanic_twice(self):
        # Positive: Try to add mechanic already on ticket (idempotent)
        payload = {
            'add_ids': [1],
            'remove_ids': []
        }
        response = self.client.put('/service_tickets/1/edit', json=payload)

        self.assertEqual(response.status_code, 200)
