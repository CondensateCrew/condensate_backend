from flask import Flask

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
      return '<h1>Condensate API</h1>'

    @app.route('/question')
    def question():
      return {
        'title': 'Question Title',
        'text': 'What is your question?'
      }

    return app
