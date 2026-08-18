import unittest
import json
from datetime import datetime


from test_base import APITestCase

class TestCustomersPost(APITestCase):
    # Tests for POST /customers - Create customer
    
    def test_create_customer_success(self):
        # Positive: Create a new customer with valid data
        payload = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone_number': '555-1234'
        }
        response = self.client.post('/customers', json=payload)
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'John Doe')
        self.assertEqual(data['email'], 'john@example.com')
        self.assertEqual(data['phone_number'], '555-1234')
    
    def test_create_customer_missing_name(self):
        # Negative: Missing required 'name' field
        payload = {
            'email': 'john@example.com',
            'phone_number': '555-1234'
        }
        response = self.client.post('/customers', json=payload)
        
        self.assertIn(response.status_code, [400, 500])
    
    def test_create_customer_missing_email(self):
        # Negative: Missing required 'email' field
        payload = {
            'name': 'John Doe',
            'phone_number': '555-1234'
        }
        response = self.client.post('/customers', json=payload)
        
        self.assertIn(response.status_code, [400, 500])
    
    def test_create_customer_missing_phone(self):
        # Negative: Missing required 'phone_number' field
        payload = {
            'name': 'John Doe',
            'email': 'john@example.com'
        }
        response = self.client.post('/customers', json=payload)
        
        self.assertIn(response.status_code, [400, 500])
    
    def test_create_customer_no_json_payload(self):
        # Negative: Request with no JSON body
        response = self.client.post('/customers')
        
        self.assertIn(response.status_code, [400, 500])
    
    def test_create_customer_invalid_json(self):
        # Negative: Request with invalid JSON
        response = self.client.post(
            '/customers',
            data='invalid json',
            content_type='application/json'
        )
        
        self.assertIn(response.status_code, [400, 500])


class TestCustomersGetAll(APITestCase):
    # Tests for GET /customers - Get all customers with pagination
    
    def test_get_all_customers_page_one(self):
        # Positive: Get first page of customers
        response = self.client.get('/customers?page=1')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('customers', data)
        self.assertIn('pagination', data)
        self.assertEqual(data['pagination']['current_page'], 1)
    
    def test_get_all_customers_default_page(self):
        # Positive: Get customers without specifying page (defaults to 1)
        response = self.client.get('/customers')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['pagination']['current_page'], 1)
    
    def test_get_all_customers_invalid_page_zero(self):
        # Negative: Request page 0 (invalid)
        response = self.client.get('/customers?page=0')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('must be 1 or greater', data['message'])
    
    def test_get_all_customers_invalid_page_negative(self):
        # Negative: Request negative page number
        response = self.client.get('/customers?page=-5')
        
        self.assertEqual(response.status_code, 400)
    
    def test_get_all_customers_page_out_of_range(self):
        # Negative: Request page that doesn't exist
        response = self.client.get('/customers?page=9999')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('does not exist', data['message'])
    
    def test_get_all_customers_non_numeric_page(self):
        # Negative: Pass non-numeric page value
        response = self.client.get('/customers?page=abc')

        self.assertIn(response.status_code, [400, 404])
    
    def test_get_all_customers_pagination_metadata(self):
        # Positive: Verify pagination metadata is correct
        response = self.client.get('/customers?page=1')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        pagination = data['pagination']
        
        self.assertIn('current_page', pagination)
        self.assertIn('total_pages', pagination)
        self.assertIn('total_customers', pagination)
        self.assertIn('customers_per_page', pagination)
        self.assertIn('has_next', pagination)
        self.assertIn('has_prev', pagination)


class TestCustomersGetById(APITestCase):
    # Tests for GET /customers/<id> - Get single customer
    
    def test_get_customer_by_id_success(self):
        # Positive: Retrieve existing customer by ID
        response = self.client.get('/customers/1')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'], 1)
    
    def test_get_customer_nonexistent_id(self):
        # Negative: Retrieve customer with non-existent ID
        response = self.client.get('/customers/9999')

        self.assertIn(response.status_code, [404, 500])
    
    def test_get_customer_invalid_id_format(self):
        # Negative: Request with invalid ID format (non-numeric)
        response = self.client.get('/customers/abc')
        
        self.assertEqual(response.status_code, 404)
    
    def test_get_customer_negative_id(self):
        # Negative: Request with negative ID
        response = self.client.get('/customers/-1')
        
        self.assertIn(response.status_code, [404, 400])
    
    def test_get_customer_zero_id(self):
        # Negative: Request with ID of 0
        response = self.client.get('/customers/0')
        
        self.assertIn(response.status_code, [404, 400])


class TestCustomersPut(APITestCase):
    # Tests for PUT /customers/<id> - Update customer
    
    def test_update_customer_success(self):
        # Positive: Update existing customer
        payload = {
            'name': 'Jane Doe',
            'email': 'jane@example.com',
            'phone_number': '555-5678'
        }
        response = self.client.put('/customers/1', json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Jane Doe')
        self.assertEqual(data['email'], 'jane@example.com')
        self.assertEqual(data['phone_number'], '555-5678')
    
    def test_update_customer_nonexistent_id(self):
        # Negative: Update non-existent customer
        payload = {
            'name': 'Jane Doe',
            'email': 'jane@example.com',
            'phone_number': '555-5678'
        }
        response = self.client.put('/customers/9999', json=payload)
        
        self.assertIn(response.status_code, [404, 500])
    
    def test_update_customer_missing_name(self):
        # Negative: Update without required 'name' field
        payload = {
            'email': 'jane@example.com',
            'phone_number': '555-5678'
        }
        response = self.client.put('/customers/1', json=payload)
        
        self.assertIn(response.status_code, [400, 500])
    
    def test_update_customer_missing_email(self):
        # Negative: Update without required 'email' field
        payload = {
            'name': 'Jane Doe',
            'phone_number': '555-5678'
        }
        response = self.client.put('/customers/1', json=payload)
        
        self.assertIn(response.status_code, [400, 500])
    
    def test_update_customer_missing_phone(self):
        # Negative: Update without required 'phone_number' field
        payload = {
            'name': 'Jane Doe',
            'email': 'jane@example.com'
        }
        response = self.client.put('/customers/1', json=payload)
        
        self.assertIn(response.status_code, [400, 500])
    
    def test_update_customer_no_json(self):
        # Negative: Update with no JSON body
        response = self.client.put('/customers/1')
        
        self.assertIn(response.status_code, [400, 500])
    
    def test_update_customer_partial_fields(self):
        # Negative: Update with incomplete field set
        payload = {
            'name': 'Jane Doe'
        }
        response = self.client.put('/customers/1', json=payload)
        
        self.assertIn(response.status_code, [400, 500])


class TestCustomersDelete(APITestCase):
    # Tests for DELETE /customers/<id> - Delete customer
    
    def test_delete_customer_success(self):
        # Positive: Delete existing customer with valid token
        response = self.client.delete(
            '/customers/1',
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        
        self.assertEqual(response.status_code, 204)
    
    def test_delete_customer_nonexistent_id(self):
        # Negative: Delete non-existent customer
        response = self.client.delete(
            '/customers/9999',
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        
        self.assertIn(response.status_code, [404, 500])
    
    def test_delete_customer_no_token(self):
        # Negative: Delete without authentication token
        response = self.client.delete('/customers/1')
        
        self.assertEqual(response.status_code, 401)
    
    def test_delete_customer_invalid_token(self):
        # Negative: Delete with invalid token
        response = self.client.delete(
            '/customers/1',
            headers={'Authorization': 'Bearer invalid_token'}
        )
        
        self.assertEqual(response.status_code, 401)
    
    def test_delete_customer_expired_token(self):
        # Negative: Delete with expired token
        response = self.client.delete(
            '/customers/1',
            headers={'Authorization': f'Bearer {self.expired_token}'}
        )
        
        self.assertEqual(response.status_code, 401)
    
    def test_delete_customer_malformed_auth_header(self):
        # Negative: Delete with malformed Authorization header
        response = self.client.delete(
            '/customers/1',
            headers={'Authorization': 'InvalidFormat'}
        )
        
        self.assertEqual(response.status_code, 401)