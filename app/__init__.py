from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from instance.config import app_config

db = SQLAlchemy()

from flask import request, jsonify, abort

def create_app(config_name):
    from app.models import User

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.route('/users', methods=['POST', 'GET'])
    def users():
        if request.method == "POST":
            name = str(request.json.get('name', ''))
            email = str(request.json.get('email', ''))
            if name:
                user = User(name=name, email=email)
                user.save()
                response = jsonify({
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'date_created': user.date_created,
                    'date_modified': user.date_modified
                })
                response.status_code = 201
                return response
        else:
            # GET
            users = User.get_all()
            results = []

            for user in users:
                obj = {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'date_created': user.date_created,
                    'date_modified': user.date_modified
                }
                results.append(obj)
            response = jsonify(results)
            response.status_code = 200
            return response

    @app.route('/users/<int:user_id>', methods=['GET'])
    def user(user_id):
        if request.method == "GET":
            users = User.query.filter_by(id=user_id)
            results = []

            for user in users:
                obj = {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'date_created': user.date_created,
                    'date_modified': user.date_modified
                }
                results.append(obj)
            response = jsonify(results)
            if results == []:
                response = jsonify({"error": "User not found."})
                response.status_code = 404
                return response
            else:
                response.status_code = 200
                return response

    return app
