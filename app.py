from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo

def create_app():
    app = Flask(__name__)
    app.config['MONGO_DBNAME'] = 'condensateDatabase'
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/condensateDatabase'
    mongo = PyMongo(app)

    @app.route('/')
    def index():
      return '<h1>Condensate API</h1>'

    @app.route('/users', methods=['GET'])
    def get_all_users():
      users = mongo.db.users
      output = []
      for u in users.find():
        output.append({'name' : u['name'], 'email' : u['email']})
      return jsonify({'result' : output})

    @app.route('/users', methods=['POST'])
    def add_user():
      users = mongo.db.users
      name = request.json['name']
      email = request.json['email']
      user_id = users.insert({'name': name, 'email': email})
      new_user = users.find_one({'_id': user_id })
      output = {'name' : new_user['name'], 'email' : new_user['email']}
      return jsonify({'result' : output})

    return app
