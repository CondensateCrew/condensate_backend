import unittest
import os
import json
from app import create_app, db


class UserTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.user = {'name': 'Ryan Hantak', 'email': 'rhantak@example.com'}

        with self.app.app_context():
            db.create_all()

    def test_user_creation(self):
        res = self.client().post('/users', json=self.user)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Ryan Hantak', str(res.data))
        self.assertIn('rhantak@example.com', str(res.data))

    def test_api_can_get_all_users(self):
        res = self.client().post('/users', json=self.user)
        self.assertEqual(res.status_code, 201)
        res = self.client().get('/users')
        self.assertEqual(res.status_code, 200)
        self.assertIn('Ryan Hantak', str(res.data))
        self.assertIn('rhantak@example.com', str(res.data))


    def test_api_can_get_user_by_id(self):
        rv = self.client().post('/users', json=self.user)
        self.assertEqual(rv.status_code, 201)
        result_in_json = json.loads(rv.data.decode('utf-8').replace("'", "\""))
        result = self.client().get(
            '/users/99')
        self.assertEqual(result.status_code, 200)
        self.assertIn('Ryan Hantak', str(result.data))
        self.assertIn('rhantak@example.com', str(result.data))

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()


if __name__ == "__main__":
    unittest.main()