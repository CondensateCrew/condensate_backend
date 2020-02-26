import unittest
import os
import json
from app import create_app, db

class DashboardTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        from app.models import User


        with self.app.app_context():
            db.create_all()

            user = User(first_name="Ryan", last_name="Hantak", email="rhantak@example.com", password="password")
            user.save()

            global user_token
            user_token = User.query.filter_by(email='rhantak@example.com').first().token

    def test_game_setup_endpoint(self):
        self.client().get('/seed')
        res = self.client().post('/game_setup', json={"token": user_token})
        data = json.loads(res.get_data(as_text=True))

        self.assertEqual(res.status_code, 200)
        assert 'word' in data[0]
        assert 'sentence' in data[0]
        assert 'sentence' in data[26]
        assert 'sentence' in data[26]

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()


if __name__ == "__main__":
    unittest.main()
