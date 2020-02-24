import unittest
import os
import json
from app import create_app, db

class DashboardTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        from app.models import User, Category, Action, Idea



        with self.app.app_context():
            db.create_all()

            user = User(first_name="Ryan", last_name="Hantak", email="rhantak@example.com", password="password")
            user.save()

            cat1 = Category(name="Finance", user_id=user.id)
            cat1.save()
            cat2 = Category(name="Education", user_id=user.id)
            cat2.save()
            cat3 = Category(name="Tech", user_id=user.id)
            cat3.save()

            action1 = Action(action="Create an app", user_id=user.id)
            action1.save()
            action2 = Action(action="Draft an ad campaign", user_id=user.id)
            action2.save()

            idea1 = Idea(user_id=user.id, random_word="Skate", action_id=action2.id, is_genius=True, question="Create an ad campaign to sell a book about financial literacy.", response="Two friends in a roller derby match are having a conversation about how they're investing their money, one tells the other about what they learned from the book and the second person is so impressed they want to buy it.")
            idea1.save()
            idea2 = Idea(user_id=user.id, random_word="Bird", action_id=action1.id, is_genius=False, question="Create an app people use to trade stocks", response="Make it easy to trade stocks mobile, charge a monthly fee so people don't feel like each trade costs them extra money and offer daily articles to encourage them to keep checking.")
            idea2.save()

            idea1.categories.append(cat1)
            idea1.categories.append(cat2)

            idea2.categories.append(cat1)
            idea2.categories.append(cat3)

            db.session.add_all([idea1, idea2])
            db.session.commit()

            global user_token
            user_token = User.query.filter_by(email='rhantak@example.com').first().token

    def test_dashboard_endpoint(self):
        res = self.client().get('/dashboard', json={"token": user_token})
        data = json.loads(res.get_data(as_text=True))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['user']['first_name'], "Ryan")
        self.assertEqual(data['user']['last_name'], "Hantak")
        self.assertEqual(data['user']['email'], "rhantak@example.com")

        self.assertEqual(len(data['brainstorms']), 2)
        self.assertEqual(data['brainstorms'][0]['action']['action'], "Draft an ad campaign")
        self.assertEqual(data['brainstorms'][0]['response'], "Two friends in a roller derby match are having a conversation about how they're investing their money, one tells the other about what they learned from the book and the second person is so impressed they want to buy it.")
        self.assertEqual(data['brainstorms'][0]['question'], "Create an ad campaign to sell a book about financial literacy.")
        self.assertEqual(data['brainstorms'][0]['isGenius'], True)
        self.assertEqual(len(data['brainstorms'][0]['categories']), 2)
        self.assertEqual(data['brainstorms'][0]['categories'][0]['name'], "Finance")
        self.assertEqual(data['brainstorms'][0]['categories'][1]['name'], "Education")

        self.assertEqual(len(data['categories']), 3)
        self.assertEqual(data['categories'][0]['name'], "Finance")
        self.assertEqual(data['categories'][1]['name'], "Education")
        self.assertEqual(data['categories'][2]['name'], "Tech")

        self.assertEqual(len(data['actions']), 2)
        self.assertEqual(data['actions'][0]['action'], "Create an app")
        self.assertEqual(data['actions'][1]['action'], "Draft an ad campaign")

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()


if __name__ == "__main__":
    unittest.main()
