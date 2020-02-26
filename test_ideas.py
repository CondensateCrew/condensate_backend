import unittest
import os
import json
from app import create_app, db

class IdeasTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        from app.models import User, Category, Action, Idea



        with self.app.app_context():
            db.create_all()

            user = User(first_name="Ryan", last_name="Hantak", email="rhantak@example.com", password="password")
            user.save()

            global user_token
            user_token = User.query.filter_by(email='rhantak@example.com').first().token

    def test_idea_post(self):
        self.client().get('/seed')
        body = {
        	"idea": "Test idea for Keanu Reevess",
        	"id": user_token,
        	"action": "Create an App",
        	"isGenius": "False",
        	"question": "Write a piece about exercise habits",
        	"categories": [{"name": "Education"}, {"name": "Technology"}]
        }
        res1 = self.client().post('/ideas', json=body)
        data1 = json.loads(res1.get_data(as_text=True))

        self.assertEqual(res1.status_code, 200)

        res2 = self.client().post('/dashboard', json={"token": user_token})
        data2 = json.loads(res2.get_data(as_text=True))

        self.assertEqual(data2['brainstorms'][0]['action']['action'], "Create an App")
        self.assertEqual(data2['brainstorms'][0]['response'], "Test idea for Keanu Reevess")
        self.assertEqual(data2['brainstorms'][0]['question'], "Write a piece about exercise habits")
        self.assertEqual(data2['brainstorms'][0]['isGenius'], False)
        self.assertEqual(len(data2['brainstorms'][0]['categories']), 2)
        self.assertEqual(data2['brainstorms'][0]['categories'][0]['name'], "Education")
        self.assertEqual(data2['brainstorms'][0]['categories'][1]['name'], "Technology")

    def test_idea_delete(self):
        self.client().get('/seed')
        body = {
        	"idea": "Test idea for Keanu Reevess",
        	"id": user_token,
        	"action": "Create an App",
        	"isGenius": "False",
        	"question": "Write a piece about exercise habits",
        	"categories": [{"name": "Education"}, {"name": "Technology"}]
        }
        self.client().post('/ideas', json=body)
        self.client().delete('/ideas', json={"token": user_token, "idea_id": 1})

        res = self.client().post('/dashboard', json={"token": user_token})
        data = json.loads(res.get_data(as_text=True))

        self.assertEqual(data['brainstorms'], [])

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()


if __name__ == "__main__":
    unittest.main()
