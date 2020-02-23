from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from instance.config import app_config

db = SQLAlchemy()

from flask import request, jsonify, abort, make_response

def create_app(config_name):
    from app.models import User
    from app.models import Word

    app = Flask(__name__, instance_relative_config=True)
    app.config['JSON_SORT_KEYS'] = False
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.route('/users', methods=['POST', 'GET'])
    def users():
        if request.method == "POST":
            first_name = str(request.json.get('first_name', ''))
            last_name = str(request.json.get('last_name', ''))
            email = str(request.json.get('email', ''))
            password_digest = str(request.json.get('password_digest', ''))
            if User.query.filter_by(email=email).count() > 0:
                abort(make_response(jsonify(message="A user with this email already exists."), 400))
            elif first_name and last_name and email and password_digest:
                user = User(first_name=first_name, last_name=last_name, email=email, password_digest=password_digest)
                user.save()
                response = jsonify({
                    'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'token': user.token,
                    'date_created': user.date_created,
                    'date_modified': user.date_modified
                })
                response.status_code = 201
                return response
            else:
                abort(make_response(jsonify(message="Missing parameter."), 400))

        else:
            # GET
            users = User.get_all()
            results = []

            for user in users:
                obj = {
                    'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'date_created': user.date_created,
                    'date_modified': user.date_modified
                }
                results.append(obj)
            response = jsonify(results)
            response.status_code = 200
            return response

    @app.route('/users/<int:user_id>')
    def user(user_id):
        users = User.query.filter_by(id=user_id)
        results = []

        for user in users:
            obj = {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
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

    @app.route('/dashboard')
    def setup():
        token = str(request.json.get('token', ''))
        if User.query.filter_by(token=token).count() > 0:
            user = User.query.filter_by(token=token).one()
            actions = []
            for action in user.actions:
                actions.append({"id": action.id, "action": action.action})
            categories = []
            for category in user.categories:
                categories.append({"id": category.id, "name": category.name})
            brainstorms = []
            for idea in user.ideas:
                bsCategories = []
                for category in idea.categories:
                    bsCategories.append({"id": category.id, "name": category.name})
                bsObj = {
                    "id": idea.id,
                    "response": idea.response,
                    "categories": bsCategories,
                    "action": {"id": idea.action.id, "action": idea.action.action},
                    "isGenius": idea.is_genius,
                    "question": idea.question
                }
                brainstorms.append(bsObj)
            # import code; code.interact(local=dict(globals(), **locals()))
            obj = {
                "user": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email
                },
                "brainstorms": brainstorms,
                "actions": actions,
                "categories": categories
            }
            response = jsonify(obj)
            return response
        else:
            abort(make_response(jsonify(message="Could not find a user with that token."), 404))

    @app.route('/import_nouns')
    def nouns():
        file = open("nouns.txt", "r")
        counter = 0
        for line in file:
            if Word.query.filter_by(word=line).count() == 0:
                dbWord = Word(word=line)
                dbWord.save()
                counter += 1

        return jsonify({"Words Added":counter})

    return app
