import pytest
import json
from datetime import datetime


class TestCustomersPost:
    # Tests for POST /customers - Create customer
    
    def test_create_customer_success(self, client, db):
        # Positive: Create a new customer with valid data
        payload = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone_number': '555-1234'
        }
        response = client.post('/customers', json=payload)
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'John Doe'
        assert data['email'] == 'john@example.com'
        assert data['phone_number'] == '555-1234'
    
    def test_create_customer_missing_name(self, client, db):
        # Negative: Missing required 'name' field
        payload = {
            'email': 'john@example.com',
            'phone_number': '555-1234'
        }
        response = client.post('/customers', json=payload)
        
        assert response.status_code in [400, 500]
    
    def test_create_customer_missing_email(self, client, db):
        # Negative: Missing required 'email' field
        payload = {
            'name': 'John Doe',
            'phone_number': '555-1234'
        }
        response = client.post('/customers', json=payload)
        
        assert response.status_code in [400, 500]
    
    def test_create_customer_missing_phone(self, client, db):
        # Negative: Missing required 'phone_number' field
        payload = {
            'name': 'John Doe',
            'email': 'john@example.com'
        }
        response = client.post('/customers', json=payload)
        
        assert response.status_code in [400, 500]
    
    def test_create_customer_no_json_payload(self, client, db):
        # Negative: Request with no JSON body
        response = client.post('/customers')
        
        assert response.status_code in [400, 500]
    
    def test_create_customer_invalid_json(self, client, db):
        # Negative: Request with invalid JSON
        response = client.post(
            '/customers',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code in [400, 500]


class TestCustomersGetAll:
    # Tests for GET /customers - Get all customers with pagination
    
    def test_get_all_customers_page_one(self, client, db, sample_customers):
        # Positive: Get first page of customers
        response = client.get('/customers?page=1')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'customers' in data
        assert 'pagination' in data
        assert data['pagination']['current_page'] == 1
    
    def test_get_all_customers_default_page(self, client, db, sample_customers):
        # Positive: Get customers without specifying page (defaults to 1)
        response = client.get('/customers')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['pagination']['current_page'] == 1
    
    def test_get_all_customers_invalid_page_zero(self, client, db):
        # Negative: Request page 0 (invalid)
        response = client.get('/customers?page=0')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'must be 1 or greater' in data['message']
    
    def test_get_all_customers_invalid_page_negative(self, client, db):
        # Negative: Request negative page number
        response = client.get('/customers?page=-5')
        
        assert response.status_code == 400
    
    def test_get_all_customers_page_out_of_range(self, client, db, sample_customers):
        # Negative: Request page that doesn't exist
        response = client.get('/customers?page=9999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'does not exist' in data['message']
    
    def test_get_all_customers_non_numeric_page(self, client, db):
        # Negative: Pass non-numeric page value
        response = client.get('/customers?page=abc')

        assert response.status_code in [400, 404]
    
    def test_get_all_customers_pagination_metadata(self, client, db, sample_customers):
        # Positive: Verify pagination metadata is correct
        response = client.get('/customers?page=1')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        pagination = data['pagination']
        
        assert 'current_page' in pagination
        assert 'total_pages' in pagination
        assert 'total_customers' in pagination
        assert 'customers_per_page' in pagination
        assert 'has_next' in pagination
        assert 'has_prev' in pagination


class TestCustomersGetById:
    # Tests for GET /customers/<id> - Get single customer
    
    def test_get_customer_by_id_success(self, client, db, sample_customers):
        # Positive: Retrieve existing customer by ID
        response = client.get('/customers/1')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == 1
    
    def test_get_customer_nonexistent_id(self, client, db):
        # Negative: Retrieve customer with non-existent ID
        response = client.get('/customers/9999')

        assert response.status_code in [404, 500]
    
    def test_get_customer_invalid_id_format(self, client, db):
        # Negative: Request with invalid ID format (non-numeric)
        response = client.get('/customers/abc')
        
        assert response.status_code == 404
    
    def test_get_customer_negative_id(self, client, db):
        # Negative: Request with negative ID
        response = client.get('/customers/-1')
        
        assert response.status_code in [404, 400]
    
    def test_get_customer_zero_id(self, client, db):
        # Negative: Request with ID of 0
        response = client.get('/customers/0')
        
        assert response.status_code in [404, 400]


class TestCustomersPut:
    # Tests for PUT /customers/<id> - Update customer
    
    def test_update_customer_success(self, client, db, sample_customers):
        # Positive: Update existing customer
        payload = {
            'name': 'Jane Doe',
            'email': 'jane@example.com',
            'phone_number': '555-5678'
        }
        response = client.put('/customers/1', json=payload)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'Jane Doe'
        assert data['email'] == 'jane@example.com'
        assert data['phone_number'] == '555-5678'
    
    def test_update_customer_nonexistent_id(self, client, db):
        # Negative: Update non-existent customer
        payload = {
            'name': 'Jane Doe',
            'email': 'jane@example.com',
            'phone_number': '555-5678'
        }
        response = client.put('/customers/9999', json=payload)
        
        assert response.status_code in [404, 500]
    
    def test_update_customer_missing_name(self, client, db, sample_customers):
        # Negative: Update without required 'name' field
        payload = {
            'email': 'jane@example.com',
            'phone_number': '555-5678'
        }
        response = client.put('/customers/1', json=payload)
        
        assert response.status_code in [400, 500]
    
    def test_update_customer_missing_email(self, client, db, sample_customers):
        # Negative: Update without required 'email' field
        payload = {
            'name': 'Jane Doe',
            'phone_number': '555-5678'
        }
        response = client.put('/customers/1', json=payload)
        
        assert response.status_code in [400, 500]
    
    def test_update_customer_missing_phone(self, client, db, sample_customers):
        # Negative: Update without required 'phone_number' field
        payload = {
            'name': 'Jane Doe',
            'email': 'jane@example.com'
        }
        response = client.put('/customers/1', json=payload)
        
        assert response.status_code in [400, 500]
    
    def test_update_customer_no_json(self, client, db, sample_customers):
        # Negative: Update with no JSON body
        response = client.put('/customers/1')
        
        assert response.status_code in [400, 500]
    
    def test_update_customer_partial_fields(self, client, db, sample_customers):
        # Negative: Update with incomplete field set
        payload = {
            'name': 'Jane Doe'
        }
        response = client.put('/customers/1', json=payload)
        
        assert response.status_code in [400, 500]


class TestCustomersDelete:
    # Tests for DELETE /customers/<id> - Delete customer
    
    def test_delete_customer_success(self, client, db, sample_customers, auth_token):
        # Positive: Delete existing customer with valid token
        response = client.delete(
            '/customers/1',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 204
    
    def test_delete_customer_nonexistent_id(self, client, db, auth_token):
        # Negative: Delete non-existent customer
        response = client.delete(
            '/customers/9999',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code in [404, 500]
    
    def test_delete_customer_no_token(self, client, db, sample_customers):
        # Negative: Delete without authentication token
        response = client.delete('/customers/1')
        
        assert response.status_code == 401
    
    def test_delete_customer_invalid_token(self, client, db, sample_customers):
        # Negative: Delete with invalid token
        response = client.delete(
            '/customers/1',
            headers={'Authorization': 'Bearer invalid_token'}
        )
        
        assert response.status_code == 401
    
    def test_delete_customer_expired_token(self, client, db, sample_customers, expired_token):
        # Negative: Delete with expired token
        response = client.delete(
            '/customers/1',
            headers={'Authorization': f'Bearer {expired_token}'}
        )
        
        assert response.status_code == 401
    
    def test_delete_customer_malformed_auth_header(self, client, db, sample_customers):
        # Negative: Delete with malformed Authorization header
        response = client.delete(
            '/customers/1',
            headers={'Authorization': 'InvalidFormat'}
        )
        
        assert response.status_code == 401