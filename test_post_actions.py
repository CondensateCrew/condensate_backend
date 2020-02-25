import unittest
import os
import json
from app import create_app, db

class UserTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.user = {'first_name': 'Ryan', 'last_name': 'Hantak', 'email': 'rhantak@example.com', 'password': 'password'}
        from app.models import User, Action

        with self.app.app_context():
            db.create_all()

            user = User(first_name="Ryan", last_name="Hantak", email="rhantak@example.com", password="password")
            user.save()

            global user_token
            user_token = User.query.filter_by(email='rhantak@example.com').first().token

    def test_adding_action(self):
        body = {"action": "Write a novel", "token": user_token}
        res = self.client().post('/actions', json=body)
        data = json.loads(res.get_data(as_text=True))

        self.assertEqual(res.status_code, 201)
        self.assertEqual(data['action'], "Write a novel")

        res2 = self.client().post('/dashboard', json={"token": user_token})
        data2 = json.loads(res2.get_data(as_text=True))

        self.assertEqual(data2['actions'][0]['action'], "Write a novel")

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
