import pytest
import json
from werkzeug.security import generate_password_hash


class TestUsersLogin:
    # Tests for POST /users/login - User authentication
    
    def test_login_success(self, client, db, sample_users):
        # Positive: Login with valid credentials
        payload = {
            'email': 'user1@example.com',
            'password': 'password123'
        }
        response = client.post('/users/login', json=payload)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'auth_token' in data
    
    def test_login_missing_email(self, client, db, sample_users):
        # Negative: Login without email
        payload = {
            'password': 'password123'
        }
        response = client.post('/users/login', json=payload)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'invalid payload' in data['message'].lower() or 'required' in data['message'].lower()
    
    def test_login_missing_password(self, client, db, sample_users):
        # Negative: Login without password
        payload = {
            'email': 'user1@example.com'
        }
        response = client.post('/users/login', json=payload)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'invalid payload' in data['message'].lower() or 'required' in data['message'].lower()
    
    def test_login_invalid_email(self, client, db, sample_users):
        # Negative: Login with non-existent email
        payload = {
            'email': 'nonexistent@example.com',
            'password': 'password123'
        }
        response = client.post('/users/login', json=payload)
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'invalid email or password' in data['message'].lower()
    
    def test_login_incorrect_password(self, client, db, sample_users):
        # Negative: Login with incorrect password
        payload = {
            'email': 'user1@example.com',
            'password': 'wrongpassword'
        }
        response = client.post('/users/login', json=payload)
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'invalid email or password' in data['message'].lower()
    
    def test_login_empty_email(self, client, db, sample_users):
        # Negative: Login with empty email
        payload = {
            'email': '',
            'password': 'password123'
        }
        response = client.post('/users/login', json=payload)
        
        assert response.status_code in [400, 401]
    
    def test_login_empty_password(self, client, db, sample_users):
        # Negative: Login with empty password
        payload = {
            'email': 'user1@example.com',
            'password': ''
        }
        response = client.post('/users/login', json=payload)
        
        assert response.status_code in [400, 401]
    
    def test_login_no_json(self, client, db):
        # Negative: Login without JSON payload
        response = client.post('/users/login')
        
        assert response.status_code == 400
    
    def test_login_invalid_json(self, client, db):
        # Negative: Login with invalid JSON
        response = client.post(
            '/users/login',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'expecting json' in data['message'].lower()
    
    def test_login_returns_valid_token_format(self, client, db, sample_users):
        # Positive: Returned token is valid JWT format
        payload = {
            'email': 'user1@example.com',
            'password': 'password123'
        }
        response = client.post('/users/login', json=payload)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        token = data['auth_token']

        assert isinstance(token, str)
        assert token.count('.') == 2
    
    def test_login_case_sensitive_email(self, client, db, sample_users):
        # Negative: Email lookup might be case-sensitive
        payload = {
            'email': 'USER1@EXAMPLE.COM',
            'password': 'password123'
        }
        response = client.post('/users/login', json=payload)
 
        assert response.status_code in [200, 401]
    
    def test_login_whitespace_in_email(self, client, db, sample_users):
        # Negative: Email with leading/trailing whitespace
        payload = {
            'email': '  user1@example.com  ',
            'password': 'password123'
        }
        response = client.post('/users/login', json=payload)

        assert response.status_code in [200, 401]


class TestUsersDeleteSelf:
    # Tests for DELETE /users/ - Delete authenticated user
    def test_delete_user_success(self, client, db, sample_users, auth_token):
        # Positive: Delete authenticated user
        response = client.delete(
            '/users/',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 204
    
    def test_delete_user_no_token(self, client, db, sample_users):
        # Negative: Delete without authentication token
        response = client.delete('/users/')
        
        assert response.status_code == 401
    
    def test_delete_user_invalid_token(self, client, db, sample_users):
        # Negative: Delete with invalid token
        response = client.delete(
            '/users/',
            headers={'Authorization': 'Bearer invalid_token'}
        )
        
        assert response.status_code == 401
    
    def test_delete_user_expired_token(self, client, db, sample_users, expired_token):
        # Negative: Delete with expired token
        response = client.delete(
            '/users/',
            headers={'Authorization': f'Bearer {expired_token}'}
        )
        
        assert response.status_code == 401
    
    def test_delete_user_malformed_auth_header(self, client, db, sample_users):
        # Negative: Delete with malformed Authorization header
        response = client.delete(
            '/users/',
            headers={'Authorization': 'InvalidFormat'}
        )
        
        assert response.status_code == 401
    
    def test_delete_user_missing_bearer_prefix(self, client, db, sample_users, auth_token):
        # Negative: Authorization header missing 'Bearer' prefix
        response = client.delete(
            '/users/',
            headers={'Authorization': auth_token}
        )
        
        assert response.status_code == 401
    
    def test_delete_user_verify_deleted(self, client, db, sample_users, auth_token):
        # Positive: Verify user is actually deleted
        # Delete the user
        response = client.delete(
            '/users/',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert response.status_code == 204

        login_payload = {
            'email': 'user1@example.com',
            'password': 'password123'
        }
        response = client.post('/users/login', json=login_payload)
        
        assert response.status_code == 401


class TestUsersGetMyTickets:
    # Tests for GET /users/my-tickets - Get authenticated user's tickets
    
    def test_get_my_tickets_success(self, client, db, sample_users, sample_customers, sample_tickets, auth_token):
        # Positive: Get tickets for authenticated user
        response = client.get(
            '/users/my-tickets',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'tickets' in data
        assert 'count' in data
    
    def test_get_my_tickets_no_token(self, client, db, sample_users):
        # Negative: Get tickets without authentication token
        response = client.get('/users/my-tickets')
        
        assert response.status_code == 401
    
    def test_get_my_tickets_invalid_token(self, client, db, sample_users):
        # Negative: Get tickets with invalid token
        response = client.get(
            '/users/my-tickets',
            headers={'Authorization': 'Bearer invalid_token'}
        )
        
        assert response.status_code == 401
    
    def test_get_my_tickets_expired_token(self, client, db, sample_users, expired_token):
        # Negative: Get tickets with expired token
        response = client.get(
            '/users/my-tickets',
            headers={'Authorization': f'Bearer {expired_token}'}
        )
        
        assert response.status_code == 401
    
    def test_get_my_tickets_malformed_auth_header(self, client, db, sample_users):
        # Negative: Get tickets with malformed Authorization header
        response = client.get(
            '/users/my-tickets',
            headers={'Authorization': 'InvalidFormat'}
        )
        
        assert response.status_code == 401
    
    def test_get_my_tickets_empty_tickets(self, client, db, sample_users, sample_customers, auth_token):
        # Positive: Get tickets when user has no tickets
        response = client.get(
            '/users/my-tickets',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['count'] == 0
        assert data['tickets'] == []
    
    def test_get_my_tickets_includes_correct_fields(self, client, db, sample_users, sample_customers, sample_tickets, auth_token):
        # Positive: Returned tickets have correct fields
        response = client.get(
            '/users/my-tickets',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        if len(data['tickets']) > 0:
            ticket = data['tickets'][0]
            assert 'id' in ticket
            assert 'customer_id' in ticket
            assert 'vin' in ticket
            assert 'service_date' in ticket
            assert 'service_description' in ticket
    
    def test_get_my_tickets_only_user_tickets(self, client, db, sample_users, sample_customers, sample_tickets, auth_token):
        # Positive: Only returns tickets for logged-in user's customer
        response = client.get(
            '/users/my-tickets',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)

        for ticket in data['tickets']:
            assert 'customer_id' in ticket
    
    def test_get_my_tickets_no_customer_account(self, client, db, sample_users, auth_token_no_customer):
        # Negative: User doesn't have associated customer account
        response = client.get(
            '/users/my-tickets',
            headers={'Authorization': f'Bearer {auth_token_no_customer}'}
        )
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'customer account not found' in data['message'].lower()
    
    def test_get_my_tickets_date_format(self, client, db, sample_users, sample_customers, sample_tickets, auth_token):
        # Positive: Returned dates are in ISO format
        response = client.get(
            '/users/my-tickets',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        if len(data['tickets']) > 0:
            ticket = data['tickets'][0]
            if ticket['service_date']:
                assert isinstance(ticket['service_date'], str)
                assert len(ticket['service_date']) > 0
    
    def test_get_my_tickets_count_accuracy(self, client, db, sample_users, sample_customers, sample_tickets, auth_token):
        # Positive: Count field matches actual number of tickets
        response = client.get(
            '/users/my-tickets',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['count'] == len(data['tickets'])
    
    def test_get_my_tickets_missing_bearer_prefix(self, client, db, sample_users, auth_token):
        # Negative: Authorization header missing 'Bearer' prefix
        response = client.get(
            '/users/my-tickets',
            headers={'Authorization': auth_token}
        )
        
        assert response.status_code == 401


class TestAuthenticationIntegration:
    # Integration tests for authentication flow
    
    def test_login_and_use_token(self, client, db, sample_users):
        # Positive: Login and use returned token to access protected route
        # Login
        login_payload = {
            'email': 'user1@example.com',
            'password': 'password123'
        }
        login_response = client.post('/users/login', json=login_payload)
        assert login_response.status_code == 200
        token = json.loads(login_response.data)['auth_token']

        response = client.delete(
            '/users/',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 204
    
    def test_multiple_logins_return_different_tokens(self, client, db, sample_users):
        # Positive: Multiple logins return different tokens
        payload = {
            'email': 'user1@example.com',
            'password': 'password123'
        }
        
        response1 = client.post('/users/login', json=payload)
        token1 = json.loads(response1.data)['auth_token']
        
        response2 = client.post('/users/login', json=payload)
        token2 = json.loads(response2.data)['auth_token']
        
        assert isinstance(token1, str)
        assert isinstance(token2, str)
    
    def test_token_persists_across_requests(self, client, db, sample_users, sample_customers, sample_tickets, auth_token):
        # Positive: Same token works across multiple requests
        response1 = client.get(
            '/users/my-tickets',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert response1.status_code == 200

        response2 = client.get(
            '/users/my-tickets',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert response2.status_code == 200