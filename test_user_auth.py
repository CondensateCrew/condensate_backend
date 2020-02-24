import unittest
import os
import json
from app import create_app, db

class UserTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.user = {'first_name': 'Ryan', 'last_name': 'Hantak', 'email': 'rhantak@example.com', 'password_digest': 'password'}

        with self.app.app_context():
            db.create_all()

    def test_user_authentication(self):
        res = self.client().get('/login', json={"email": "rhantak@example.com", "password_digest": "password"})
        data = json.loads(res.get_data(as_text=True))

        self.assertEqual(res.status_code, 303)
        self.assertEqual(len(data['token']), 32)

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
