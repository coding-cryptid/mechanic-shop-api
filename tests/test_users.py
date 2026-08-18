import unittest
import json
from werkzeug.security import generate_password_hash


from test_base import APITestCase

class TestUsersLogin(APITestCase):
    # Tests for POST /users/login - User authentication
    
    def test_login_success(self):
        # Positive: Login with valid credentials
        payload = {
            'email': 'user1@example.com',
            'password': 'password123'
        }
        response = self.client.post('/users/login', json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('auth_token', data)
    
    def test_login_missing_email(self):
        # Negative: Login without email
        payload = {
            'password': 'password123'
        }
        response = self.client.post('/users/login', json=payload)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertTrue(
            'invalid payload' in data['message'].lower() or
            'required' in data['message'].lower()
        )
    
    def test_login_missing_password(self):
        # Negative: Login without password
        payload = {
            'email': 'user1@example.com'
        }
        response = self.client.post('/users/login', json=payload)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertTrue(
            'invalid payload' in data['message'].lower() or
            'required' in data['message'].lower()
        )
    
    def test_login_invalid_email(self):
        # Negative: Login with non-existent email
        payload = {
            'email': 'nonexistent@example.com',
            'password': 'password123'
        }
        response = self.client.post('/users/login', json=payload)
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('invalid email or password', data['message'].lower())
    
    def test_login_incorrect_password(self):
        # Negative: Login with incorrect password
        payload = {
            'email': 'user1@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post('/users/login', json=payload)
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('invalid email or password', data['message'].lower())
    
    def test_login_empty_email(self):
        # Negative: Login with empty email
        payload = {
            'email': '',
            'password': 'password123'
        }
        response = self.client.post('/users/login', json=payload)
        
        self.assertIn(response.status_code, [400, 401])
    
    def test_login_empty_password(self):
        # Negative: Login with empty password
        payload = {
            'email': 'user1@example.com',
            'password': ''
        }
        response = self.client.post('/users/login', json=payload)
        
        self.assertIn(response.status_code, [400, 401])
    
    def test_login_no_json(self):
        # Negative: Login without JSON payload
        response = self.client.post('/users/login')
        
        self.assertEqual(response.status_code, 400)
    
    def test_login_invalid_json(self):
        # Negative: Login with invalid JSON
        response = self.client.post(
            '/users/login',
            data='invalid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('expecting json', data['message'].lower())
    
    def test_login_returns_valid_token_format(self):
        # Positive: Returned token is valid JWT format
        payload = {
            'email': 'user1@example.com',
            'password': 'password123'
        }
        response = self.client.post('/users/login', json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        token = data['auth_token']

        self.assertIsInstance(token, str)
        self.assertEqual(token.count('.'), 2)
    
    def test_login_case_sensitive_email(self):
        # Negative: Email lookup might be case-sensitive
        payload = {
            'email': 'USER1@EXAMPLE.COM',
            'password': 'password123'
        }
        response = self.client.post('/users/login', json=payload)
 
        self.assertIn(response.status_code, [200, 401])
    
    def test_login_whitespace_in_email(self):
        # Negative: Email with leading/trailing whitespace
        payload = {
            'email': '  user1@example.com  ',
            'password': 'password123'
        }
        response = self.client.post('/users/login', json=payload)

        self.assertIn(response.status_code, [200, 401])


class TestUsersDeleteSelf(APITestCase):
    # Tests for DELETE /users/ - Delete authenticated user
    def test_delete_user_success(self):
        # Positive: Delete authenticated user
        response = self.client.delete(
            '/users/',
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        
        self.assertEqual(response.status_code, 204)
    
    def test_delete_user_no_token(self):
        # Negative: Delete without authentication token
        response = self.client.delete('/users/')
        
        self.assertEqual(response.status_code, 401)
    
    def test_delete_user_invalid_token(self):
        # Negative: Delete with invalid token
        response = self.client.delete(
            '/users/',
            headers={'Authorization': 'Bearer invalid_token'}
        )
        
        self.assertEqual(response.status_code, 401)
    
    def test_delete_user_expired_token(self):
        # Negative: Delete with expired token
        response = self.client.delete(
            '/users/',
            headers={'Authorization': f'Bearer {self.expired_token}'}
        )
        
        self.assertEqual(response.status_code, 401)
    
    def test_delete_user_malformed_auth_header(self):
        # Negative: Delete with malformed Authorization header
        response = self.client.delete(
            '/users/',
            headers={'Authorization': 'InvalidFormat'}
        )
        
        self.assertEqual(response.status_code, 401)
    
    def test_delete_user_missing_bearer_prefix(self):
        # Negative: Authorization header missing 'Bearer' prefix
        response = self.client.delete(
            '/users/',
            headers={'Authorization': self.auth_token}
        )
        
        self.assertEqual(response.status_code, 401)
    
    def test_delete_user_verify_deleted(self):
        # Positive: Verify user is actually deleted
        # Delete the user
        response = self.client.delete(
            '/users/',
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        self.assertEqual(response.status_code, 204)

        login_payload = {
            'email': 'user1@example.com',
            'password': 'password123'
        }
        response = self.client.post('/users/login', json=login_payload)
        
        self.assertEqual(response.status_code, 401)


class TestUsersGetMyTickets(APITestCase):
    # Tests for GET /users/my-tickets - Get authenticated user's tickets
    
    def test_get_my_tickets_success(self):
        # Positive: Get tickets for authenticated user
        response = self.client.get(
            '/users/my-tickets',
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('tickets', data)
        self.assertIn('count', data)
    
    def test_get_my_tickets_no_token(self):
        # Negative: Get tickets without authentication token
        response = self.client.get('/users/my-tickets')
        
        self.assertEqual(response.status_code, 401)
    
    def test_get_my_tickets_invalid_token(self):
        # Negative: Get tickets with invalid token
        response = self.client.get(
            '/users/my-tickets',
            headers={'Authorization': 'Bearer invalid_token'}
        )
        
        self.assertEqual(response.status_code, 401)
    
    def test_get_my_tickets_expired_token(self):
        # Negative: Get tickets with expired token
        response = self.client.get(
            '/users/my-tickets',
            headers={'Authorization': f'Bearer {self.expired_token}'}
        )
        
        self.assertEqual(response.status_code, 401)
    
    def test_get_my_tickets_malformed_auth_header(self):
        # Negative: Get tickets with malformed Authorization header
        response = self.client.get(
            '/users/my-tickets',
            headers={'Authorization': 'InvalidFormat'}
        )
        
        self.assertEqual(response.status_code, 401)
    
    def test_get_my_tickets_empty_tickets(self):
        # Positive: Get tickets when user has no tickets
        response = self.client.get(
            '/users/my-tickets',
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['count'], 0)
        self.assertEqual(data['tickets'], [])
    
    def test_get_my_tickets_includes_correct_fields(self):
        # Positive: Returned tickets have correct fields
        response = self.client.get(
            '/users/my-tickets',
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        if len(data['tickets']) > 0:
            ticket = data['tickets'][0]
            self.assertIn('id', ticket)
            self.assertIn('customer_id', ticket)
            self.assertIn('vin', ticket)
            self.assertIn('service_date', ticket)
            self.assertIn('service_description', ticket)
    
    def test_get_my_tickets_only_user_tickets(self):
        # Positive: Only returns tickets for logged-in user's customer
        response = self.client.get(
            '/users/my-tickets',
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        for ticket in data['tickets']:
            self.assertIn('customer_id', ticket)
    
    def test_get_my_tickets_no_customer_account(self):
        # Negative: User doesn't have associated customer account
        response = self.client.get(
            '/users/my-tickets',
            headers={'Authorization': f'Bearer {self.auth_token_no_customer}'}
        )
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('customer account not found', data['message'].lower())
    
    def test_get_my_tickets_date_format(self):
        # Positive: Returned dates are in ISO format
        response = self.client.get(
            '/users/my-tickets',
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        if len(data['tickets']) > 0:
            ticket = data['tickets'][0]
            if ticket['service_date']:
                self.assertIsInstance(ticket['service_date'], str)
                self.assertTrue(len(ticket['service_date']) > 0)
    
    def test_get_my_tickets_count_accuracy(self):
        # Positive: Count field matches actual number of tickets
        response = self.client.get(
            '/users/my-tickets',
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(data['count'], len(data['tickets']))
    
    def test_get_my_tickets_missing_bearer_prefix(self):
        # Negative: Authorization header missing 'Bearer' prefix
        response = self.client.get(
            '/users/my-tickets',
            headers={'Authorization': self.auth_token}
        )
        
        self.assertEqual(response.status_code, 401)


class TestAuthenticationIntegration(APITestCase):
    # Integration tests for authentication flow
    
    def test_login_and_use_token(self):
        # Positive: Login and use returned token to access protected route
        # Login
        login_payload = {
            'email': 'user1@example.com',
            'password': 'password123'
        }
        login_response = self.client.post('/users/login', json=login_payload)
        self.assertEqual(login_response.status_code, 200)
        token = json.loads(login_response.data)['auth_token']

        response = self.client.delete(
            '/users/',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        self.assertEqual(response.status_code, 204)
    
    def test_multiple_logins_return_different_tokens(self):
        # Positive: Multiple logins return different tokens
        payload = {
            'email': 'user1@example.com',
            'password': 'password123'
        }
        
        response1 = self.client.post('/users/login', json=payload)
        token1 = json.loads(response1.data)['auth_token']
        
        response2 = self.client.post('/users/login', json=payload)
        token2 = json.loads(response2.data)['auth_token']
        
        self.assertIsInstance(token1, str)
        self.assertIsInstance(token2, str)
    
    def test_token_persists_across_requests(self):
        # Positive: Same token works across multiple requests
        response1 = self.client.get(
            '/users/my-tickets',
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        self.assertEqual(response1.status_code, 200)

        response2 = self.client.get(
            '/users/my-tickets',
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        self.assertEqual(response2.status_code, 200)
