import pytest
from flask import url_for

class TestApp:

    def test_question(self, client):
        res = client.get(url_for('question'))
        assert res.status_code == 200
        assert res.json == {
          'title': 'Question Title',
          'text': 'What is your question?'
        }
