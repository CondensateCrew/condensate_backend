from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
  return '<h1>Condensate API</h1>'

@app.route('/question')
def recipes():
  return {
    'title': 'Question Title',
    'text': 'What is your question?'
  }
