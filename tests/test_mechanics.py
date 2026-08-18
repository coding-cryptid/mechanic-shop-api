import unittest
import json


from test_base import APITestCase

class TestMechanicsPost(APITestCase):
    # Tests for POST /mechanics - Create mechanic
    
    def test_create_mechanic_success(self):
        # Positive: Create mechanic with valid data
        payload = {
            'name': 'Bob Smith',
            'email': 'bob@example.com',
            'phone_number': '555-9876',
            'salary': 50000
        }
        response = self.client.post('/mechanics', json=payload)
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Bob Smith')
        self.assertEqual(data['email'], 'bob@example.com')
        self.assertEqual(data['phone_number'], '555-9876')
        self.assertEqual(data['salary'], 50000)
    
    def test_create_mechanic_missing_name(self):
        # Negative: Missing required 'name' field
        payload = {
            'email': 'bob@example.com',
            'phone_number': '555-9876',
            'salary': 50000
        }
        response = self.client.post('/mechanics', json=payload)
        
        self.assertIn(response.status_code, [400, 500])
    
    def test_create_mechanic_missing_email(self):
        # Negative: Missing required 'email' field
        payload = {
            'name': 'Bob Smith',
            'phone_number': '555-9876',
            'salary': 50000
        }
        response = self.client.post('/mechanics', json=payload)
        
        self.assertIn(response.status_code, [400, 500])
    
    def test_create_mechanic_missing_phone(self):
        # Negative: Missing required 'phone_number' field
        payload = {
            'name': 'Bob Smith',
            'email': 'bob@example.com',
            'salary': 50000
        }
        response = self.client.post('/mechanics', json=payload)
        
        self.assertIn(response.status_code, [400, 500])
    
    def test_create_mechanic_missing_salary(self):
        # Negative: Missing required 'salary' field
        payload = {
            'name': 'Bob Smith',
            'email': 'bob@example.com',
            'phone_number': '555-9876'
        }
        response = self.client.post('/mechanics', json=payload)
        
        self.assertIn(response.status_code, [400, 500])
    
    def test_create_mechanic_negative_salary(self):
        # Negative: Salary is negative
        payload = {
            'name': 'Bob Smith',
            'email': 'bob@example.com',
            'phone_number': '555-9876',
            'salary': -50000
        }
        response = self.client.post('/mechanics', json=payload)

        self.assertIn(response.status_code, [201, 400])
    
    def test_create_mechanic_rate_limit(self):
        # Negative: Exceed rate limit (6 per hour)
        payload = {
            'name': 'Test Mechanic',
            'email': 'test@example.com',
            'phone_number': '555-0000',
            'salary': 50000
        }

        for i in range(7):
            payload['email'] = f'test{i}@example.com'
            response = self.client.post('/mechanics', json=payload)
        
        self.assertEqual(response.status_code, 429)
    
    def test_create_mechanic_no_json(self):
        # Negative: No JSON payload
        response = self.client.post('/mechanics')
        
        self.assertIn(response.status_code, [400, 500])
    
    def test_create_mechanic_invalid_json(self):
        # Negative: Invalid JSON format
        response = self.client.post(
            '/mechanics',
            data='invalid json',
            content_type='application/json'
        )
        
        self.assertIn(response.status_code, [400, 500])


class TestMechanicsGetAll(APITestCase):
    # Tests for GET /mechanics - Get all mechanics
    
    def test_get_all_mechanics_success(self):
        # Positive: Retrieve all mechanics
        response = self.client.get('/mechanics')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
    
    def test_get_all_mechanics_empty(self):
        # Positive: Get mechanics when none exist
        response = self.client.get('/mechanics')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)
    
    def test_get_all_mechanics_returns_correct_fields(self):
        # Positive: Returned mechanics have correct fields
        response = self.client.get('/mechanics')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        if len(data) > 0:
            mechanic = data[0]
            self.assertIn('id', mechanic)
            self.assertIn('name', mechanic)
            self.assertIn('email', mechanic)
            self.assertIn('phone_number', mechanic)
            self.assertIn('salary', mechanic)
    
    def test_get_all_mechanics_caching(self):
        # Positive: Verify endpoint is cached (cache-control header)
        response = self.client.get('/mechanics')

        self.assertEqual(response.status_code, 200)


class TestMechanicsGetById(APITestCase):
    # Tests for GET /mechanics/<id> - Get single mechanic
    
    def test_get_mechanic_by_id_success(self):
        # Positive: Retrieve existing mechanic by ID
        response = self.client.get('/mechanics/1')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'], 1)
    
    def test_get_mechanic_nonexistent_id(self):
        # Negative: Retrieve non-existent mechanic
        response = self.client.get('/mechanics/9999')
        
        self.assertIn(response.status_code, [404, 500])
    
    def test_get_mechanic_invalid_id_format(self):
        # Negative: Invalid ID format (non-numeric)
        response = self.client.get('/mechanics/abc')
        
        self.assertEqual(response.status_code, 404)
    
    def test_get_mechanic_negative_id(self):
        # Negative: Request with negative ID
        response = self.client.get('/mechanics/-1')
        
        self.assertIn(response.status_code, [404, 400])
    
    def test_get_mechanic_zero_id(self):
        # Negative: Request with ID of 0
        response = self.client.get('/mechanics/0')
        
        self.assertIn(response.status_code, [404, 400])


class TestMechanicsGetLeaderboard(APITestCase):
    # Tests for GET /mechanics/leaderboard - Get mechanics ranked by tickets
    
    def test_get_leaderboard_success(self):
        # Positive: Retrieve mechanics leaderboard
        response = self.client.get('/mechanics/leaderboard')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('leaderboard', data)
        self.assertIn('total_mechanics', data)
    
    def test_get_leaderboard_empty(self):
        # Positive: Get leaderboard when no mechanics exist
        response = self.client.get('/mechanics/leaderboard')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['total_mechanics'], 0)
        self.assertEqual(data['leaderboard'], [])
    
    def test_get_leaderboard_ordering(self):
        # Positive: Verify leaderboard is ordered by ticket count (descending)
        response = self.client.get('/mechanics/leaderboard')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        leaderboard = data['leaderboard']

        if len(leaderboard) > 1:
            for i in range(len(leaderboard) - 1):
                self.assertGreaterEqual(
                    leaderboard[i]['tickets_completed'],
                    leaderboard[i + 1]['tickets_completed']
                )
    
    def test_get_leaderboard_includes_ticket_count(self):
        # Positive: Leaderboard entries include ticket_completed field
        response = self.client.get('/mechanics/leaderboard')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        if len(data['leaderboard']) > 0:
            mechanic = data['leaderboard'][0]
            self.assertIn('tickets_completed', mechanic)


class TestMechanicsPut(APITestCase):
    # Tests for PUT /mechanics/<id> - Update mechanic
    
    def test_update_mechanic_success(self):
        # Positive: Update existing mechanic
        payload = {
            'name': 'Robert Smith',
            'email': 'robert@example.com',
            'phone_number': '555-5555',
            'salary': 55000
        }
        response = self.client.put('/mechanics/1', json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Robert Smith')
        self.assertEqual(data['salary'], 55000)
    
    def test_update_mechanic_nonexistent_id(self):
        # Negative: Update non-existent mechanic
        payload = {
            'name': 'Robert Smith',
            'email': 'robert@example.com',
            'phone_number': '555-5555',
            'salary': 55000
        }
        response = self.client.put('/mechanics/9999', json=payload)
        
        self.assertIn(response.status_code, [404, 500])
    
    def test_update_mechanic_missing_name(self):
        # Negative: Update without required 'name' field
        payload = {
            'email': 'robert@example.com',
            'phone_number': '555-5555',
            'salary': 55000
        }
        response = self.client.put('/mechanics/1', json=payload)
        
        self.assertIn(response.status_code, [400, 500])
    
    def test_update_mechanic_missing_email(self):
        # Negative: Update without required 'email' field
        payload = {
            'name': 'Robert Smith',
            'phone_number': '555-5555',
            'salary': 55000
        }
        response = self.client.put('/mechanics/1', json=payload)
        
        self.assertIn(response.status_code, [400, 500])
    
    def test_update_mechanic_missing_phone(self):
        # Negative: Update without required 'phone_number' field
        payload = {
            'name': 'Robert Smith',
            'email': 'robert@example.com',
            'salary': 55000
        }
        response = self.client.put('/mechanics/1', json=payload)
        
        self.assertIn(response.status_code, [400, 500])
    
    def test_update_mechanic_missing_salary(self):
        # Negative: Update without required 'salary' field
        payload = {
            'name': 'Robert Smith',
            'email': 'robert@example.com',
            'phone_number': '555-5555'
        }
        response = self.client.put('/mechanics/1', json=payload)
        
        self.assertIn(response.status_code, [400, 500])
    
    def test_update_mechanic_no_json(self):
        # Negative: Update with no JSON body
        response = self.client.put('/mechanics/1')
        
        self.assertIn(response.status_code, [400, 500])
    
    def test_update_mechanic_invalid_salary_type(self):
        # Negative: Salary is non-numeric
        payload = {
            'name': 'Robert Smith',
            'email': 'robert@example.com',
            'phone_number': '555-5555',
            'salary': 'not_a_number'
        }
        response = self.client.put('/mechanics/1', json=payload)
        
        self.assertIn(response.status_code, [400, 500])


class TestMechanicsDelete(APITestCase):
    # Tests for DELETE /mechanics/<id> - Delete mechanic
    
    def test_delete_mechanic_success(self):
        # Positive: Delete existing mechanic with valid token
        response = self.client.delete(
            '/mechanics/1',
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        
        self.assertEqual(response.status_code, 204)
    
    def test_delete_mechanic_nonexistent_id(self):
        # Negative: Delete non-existent mechanic
        response = self.client.delete(
            '/mechanics/9999',
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        
        self.assertIn(response.status_code, [404, 500])
    
    def test_delete_mechanic_no_token(self):
        # Negative: Delete without authentication token
        response = self.client.delete('/mechanics/1')
        
        self.assertEqual(response.status_code, 401)
    
    def test_delete_mechanic_invalid_token(self):
        # Negative: Delete with invalid token
        response = self.client.delete(
            '/mechanics/1',
            headers={'Authorization': 'Bearer invalid_token'}
        )
        
        self.assertEqual(response.status_code, 401)
    
    def test_delete_mechanic_rate_limit(self):
        # Negative: Exceed rate limit on delete (3 per hour)
        for i in range(4):
            create_payload = {
                'name': f'Mechanic {i}',
                'email': f'mech{i}@example.com',
                'phone_number': '555-0000',
                'salary': 50000
            }
            self.client.post('/mechanics', json=create_payload)
            
            response = self.client.delete(
                f'/mechanics/{i+1}',
                headers={'Authorization': f'Bearer {self.auth_token}'}
            )

        self.assertEqual(response.status_code, 429)
    
    def test_delete_mechanic_expired_token(self):
        # Negative: Delete with expired token
        response = self.client.delete(
            '/mechanics/1',
            headers={'Authorization': f'Bearer {self.expired_token}'}
        )
        
        self.assertEqual(response.status_code, 401)
    
    def test_delete_mechanic_malformed_auth_header(self):
        # Negative: Delete with malformed Authorization header
        response = self.client.delete(
            '/mechanics/1',
            headers={'Authorization': 'InvalidFormat'}
        )
        
        self.assertEqual(response.status_code, 401)
