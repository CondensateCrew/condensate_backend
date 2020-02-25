import unittest
import os
import json
from app import create_app, db


class UserTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.user = {'first_name': 'Ryan', 'last_name': 'Hantak', 'email': 'rhantak@example.com', 'password': 'password'}

        with self.app.app_context():
            db.create_all()

    def test_user_creation(self):
        res = self.client().post('/users', json=self.user)
        data = json.loads(res.get_data(as_text=True))

        self.assertEqual(len(data['token']), 32)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Ryan', str(res.data))
        self.assertIn('Hantak', str(res.data))
        self.assertIn('rhantak@example.com', str(res.data))

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()


if __name__ == "__main__":
    unittest.main()
