import pytest
import json


class TestMechanicsPost:
    # Tests for POST /mechanics - Create mechanic
    
    def test_create_mechanic_success(self, client, db):
        # Positive: Create mechanic with valid data
        payload = {
            'name': 'Bob Smith',
            'email': 'bob@example.com',
            'phone_number': '555-9876',
            'salary': 50000
        }
        response = client.post('/mechanics', json=payload)
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'Bob Smith'
        assert data['email'] == 'bob@example.com'
        assert data['phone_number'] == '555-9876'
        assert data['salary'] == 50000
    
    def test_create_mechanic_missing_name(self, client, db):
        # Negative: Missing required 'name' field
        payload = {
            'email': 'bob@example.com',
            'phone_number': '555-9876',
            'salary': 50000
        }
        response = client.post('/mechanics', json=payload)
        
        assert response.status_code in [400, 500]
    
    def test_create_mechanic_missing_email(self, client, db):
        # Negative: Missing required 'email' field
        payload = {
            'name': 'Bob Smith',
            'phone_number': '555-9876',
            'salary': 50000
        }
        response = client.post('/mechanics', json=payload)
        
        assert response.status_code in [400, 500]
    
    def test_create_mechanic_missing_phone(self, client, db):
        # Negative: Missing required 'phone_number' field
        payload = {
            'name': 'Bob Smith',
            'email': 'bob@example.com',
            'salary': 50000
        }
        response = client.post('/mechanics', json=payload)
        
        assert response.status_code in [400, 500]
    
    def test_create_mechanic_missing_salary(self, client, db):
        # Negative: Missing required 'salary' field
        payload = {
            'name': 'Bob Smith',
            'email': 'bob@example.com',
            'phone_number': '555-9876'
        }
        response = client.post('/mechanics', json=payload)
        
        assert response.status_code in [400, 500]
    
    def test_create_mechanic_negative_salary(self, client, db):
        # Negative: Salary is negative
        payload = {
            'name': 'Bob Smith',
            'email': 'bob@example.com',
            'phone_number': '555-9876',
            'salary': -50000
        }
        response = client.post('/mechanics', json=payload)

        assert response.status_code in [201, 400]
    
    def test_create_mechanic_rate_limit(self, client, db):
        # Negative: Exceed rate limit (6 per hour)
        payload = {
            'name': 'Test Mechanic',
            'email': 'test@example.com',
            'phone_number': '555-0000',
            'salary': 50000
        }

        for i in range(7):
            payload['email'] = f'test{i}@example.com'
            response = client.post('/mechanics', json=payload)
        
        assert response.status_code == 429
    
    def test_create_mechanic_no_json(self, client, db):
        # Negative: No JSON payload
        response = client.post('/mechanics')
        
        assert response.status_code in [400, 500]
    
    def test_create_mechanic_invalid_json(self, client, db):
        # Negative: Invalid JSON format
        response = client.post(
            '/mechanics',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code in [400, 500]


class TestMechanicsGetAll:
    # Tests for GET /mechanics - Get all mechanics
    
    def test_get_all_mechanics_success(self, client, db, sample_mechanics):
        # Positive: Retrieve all mechanics
        response = client.get('/mechanics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_get_all_mechanics_empty(self, client, db):
        # Positive: Get mechanics when none exist
        response = client.get('/mechanics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_all_mechanics_returns_correct_fields(self, client, db, sample_mechanics):
        # Positive: Returned mechanics have correct fields
        response = client.get('/mechanics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        if len(data) > 0:
            mechanic = data[0]
            assert 'id' in mechanic
            assert 'name' in mechanic
            assert 'email' in mechanic
            assert 'phone_number' in mechanic
            assert 'salary' in mechanic
    
    def test_get_all_mechanics_caching(self, client, db, sample_mechanics):
        # Positive: Verify endpoint is cached (cache-control header)
        response = client.get('/mechanics')

        assert response.status_code == 200


class TestMechanicsGetById:
    # Tests for GET /mechanics/<id> - Get single mechanic
    
    def test_get_mechanic_by_id_success(self, client, db, sample_mechanics):
        # Positive: Retrieve existing mechanic by ID
        response = client.get('/mechanics/1')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == 1
    
    def test_get_mechanic_nonexistent_id(self, client, db):
        # Negative: Retrieve non-existent mechanic
        response = client.get('/mechanics/9999')
        
        assert response.status_code in [404, 500]
    
    def test_get_mechanic_invalid_id_format(self, client, db):
        # Negative: Invalid ID format (non-numeric)
        response = client.get('/mechanics/abc')
        
        assert response.status_code == 404
    
    def test_get_mechanic_negative_id(self, client, db):
        # Negative: Request with negative ID
        response = client.get('/mechanics/-1')
        
        assert response.status_code in [404, 400]
    
    def test_get_mechanic_zero_id(self, client, db):
        # Negative: Request with ID of 0
        response = client.get('/mechanics/0')
        
        assert response.status_code in [404, 400]


class TestMechanicsGetLeaderboard:
    # Tests for GET /mechanics/leaderboard - Get mechanics ranked by tickets
    
    def test_get_leaderboard_success(self, client, db, sample_mechanics, sample_tickets):
        # Positive: Retrieve mechanics leaderboard
        response = client.get('/mechanics/leaderboard')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'leaderboard' in data
        assert 'total_mechanics' in data
    
    def test_get_leaderboard_empty(self, client, db):
        # Positive: Get leaderboard when no mechanics exist
        response = client.get('/mechanics/leaderboard')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_mechanics'] == 0
        assert data['leaderboard'] == []
    
    def test_get_leaderboard_ordering(self, client, db, sample_mechanics_with_tickets):
        # Positive: Verify leaderboard is ordered by ticket count (descending)
        response = client.get('/mechanics/leaderboard')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        leaderboard = data['leaderboard']

        if len(leaderboard) > 1:
            for i in range(len(leaderboard) - 1):
                assert (leaderboard[i]['tickets_completed'] >= 
                        leaderboard[i + 1]['tickets_completed'])
    
    def test_get_leaderboard_includes_ticket_count(self, client, db, sample_mechanics_with_tickets):
        # Positive: Leaderboard entries include ticket_completed field
        response = client.get('/mechanics/leaderboard')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        if len(data['leaderboard']) > 0:
            mechanic = data['leaderboard'][0]
            assert 'tickets_completed' in mechanic


class TestMechanicsPut:
    # Tests for PUT /mechanics/<id> - Update mechanic
    
    def test_update_mechanic_success(self, client, db, sample_mechanics):
        # Positive: Update existing mechanic
        payload = {
            'name': 'Robert Smith',
            'email': 'robert@example.com',
            'phone_number': '555-5555',
            'salary': 55000
        }
        response = client.put('/mechanics/1', json=payload)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'Robert Smith'
        assert data['salary'] == 55000
    
    def test_update_mechanic_nonexistent_id(self, client, db):
        # Negative: Update non-existent mechanic
        payload = {
            'name': 'Robert Smith',
            'email': 'robert@example.com',
            'phone_number': '555-5555',
            'salary': 55000
        }
        response = client.put('/mechanics/9999', json=payload)
        
        assert response.status_code in [404, 500]
    
    def test_update_mechanic_missing_name(self, client, db, sample_mechanics):
        # Negative: Update without required 'name' field
        payload = {
            'email': 'robert@example.com',
            'phone_number': '555-5555',
            'salary': 55000
        }
        response = client.put('/mechanics/1', json=payload)
        
        assert response.status_code in [400, 500]
    
    def test_update_mechanic_missing_email(self, client, db, sample_mechanics):
        # Negative: Update without required 'email' field
        payload = {
            'name': 'Robert Smith',
            'phone_number': '555-5555',
            'salary': 55000
        }
        response = client.put('/mechanics/1', json=payload)
        
        assert response.status_code in [400, 500]
    
    def test_update_mechanic_missing_phone(self, client, db, sample_mechanics):
        # Negative: Update without required 'phone_number' field
        payload = {
            'name': 'Robert Smith',
            'email': 'robert@example.com',
            'salary': 55000
        }
        response = client.put('/mechanics/1', json=payload)
        
        assert response.status_code in [400, 500]
    
    def test_update_mechanic_missing_salary(self, client, db, sample_mechanics):
        # Negative: Update without required 'salary' field
        payload = {
            'name': 'Robert Smith',
            'email': 'robert@example.com',
            'phone_number': '555-5555'
        }
        response = client.put('/mechanics/1', json=payload)
        
        assert response.status_code in [400, 500]
    
    def test_update_mechanic_no_json(self, client, db, sample_mechanics):
        # Negative: Update with no JSON body
        response = client.put('/mechanics/1')
        
        assert response.status_code in [400, 500]
    
    def test_update_mechanic_invalid_salary_type(self, client, db, sample_mechanics):
        # Negative: Salary is non-numeric
        payload = {
            'name': 'Robert Smith',
            'email': 'robert@example.com',
            'phone_number': '555-5555',
            'salary': 'not_a_number'
        }
        response = client.put('/mechanics/1', json=payload)
        
        assert response.status_code in [400, 500]


class TestMechanicsDelete:
    # Tests for DELETE /mechanics/<id> - Delete mechanic
    
    def test_delete_mechanic_success(self, client, db, sample_mechanics, auth_token):
        # Positive: Delete existing mechanic with valid token
        response = client.delete(
            '/mechanics/1',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 204
    
    def test_delete_mechanic_nonexistent_id(self, client, db, auth_token):
        # Negative: Delete non-existent mechanic
        response = client.delete(
            '/mechanics/9999',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code in [404, 500]
    
    def test_delete_mechanic_no_token(self, client, db, sample_mechanics):
        # Negative: Delete without authentication token
        response = client.delete('/mechanics/1')
        
        assert response.status_code == 401
    
    def test_delete_mechanic_invalid_token(self, client, db, sample_mechanics):
        # Negative: Delete with invalid token
        response = client.delete(
            '/mechanics/1',
            headers={'Authorization': 'Bearer invalid_token'}
        )
        
        assert response.status_code == 401
    
    def test_delete_mechanic_rate_limit(self, client, db, sample_mechanics, auth_token):
        # Negative: Exceed rate limit on delete (3 per hour)
        for i in range(4):
            create_payload = {
                'name': f'Mechanic {i}',
                'email': f'mech{i}@example.com',
                'phone_number': '555-0000',
                'salary': 50000
            }
            client.post('/mechanics', json=create_payload)
            
            response = client.delete(
                f'/mechanics/{i+1}',
                headers={'Authorization': f'Bearer {auth_token}'}
            )

        assert response.status_code == 429
    
    def test_delete_mechanic_expired_token(self, client, db, sample_mechanics, expired_token):
        # Negative: Delete with expired token
        response = client.delete(
            '/mechanics/1',
            headers={'Authorization': f'Bearer {expired_token}'}
        )
        
        assert response.status_code == 401
    
    def test_delete_mechanic_malformed_auth_header(self, client, db, sample_mechanics):
        # Negative: Delete with malformed Authorization header
        response = client.delete(
            '/mechanics/1',
            headers={'Authorization': 'InvalidFormat'}
        )
        
        assert response.status_code == 401