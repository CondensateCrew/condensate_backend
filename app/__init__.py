from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from instance.config import app_config
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()

from flask import request, jsonify, abort, make_response
from sqlalchemy.sql.expression import func, select
import requests
import random
import os

def create_app(config_name):
    from app.models import User
    from app.models import Word
    from app.models import Sentence
    from app.models import Action
    from app.models import Idea
    from app.models import Category
    from app.models import idea_categories

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
            password = str(request.json.get('password', ''))
            if User.query.filter_by(email=email).count() > 0:
                abort(make_response(jsonify(message="A user with this email already exists."), 400))
            elif first_name and last_name and email and password:
                user = User(first_name=first_name, last_name=last_name, email=email, password=password)
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
    def dashboard():
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

    @app.route('/game_setup')
    def setup():
        def find_sentence(word):
            if len(word.sentence) < 3:
                url = "https://twinword-word-graph-dictionary.p.rapidapi.com/example/"
                querystring = {"entry":word.word[:-1]}
                headers = {
                    'x-rapidapi-host': "twinword-word-graph-dictionary.p.rapidapi.com",
                    'x-rapidapi-key': os.getenv('RAPID_API_KEY')
                    }
                response = requests.request("GET", url, headers=headers, params=querystring)
                raw_sentence_response = response.json()
                while True:
                    index_choice = random.choice(range(len(raw_sentence_response["example"])))
                    sentence_response = raw_sentence_response["example"][index_choice]
                    if Sentence.query.filter_by(example=sentence_response).count() == 0:
                        break

                sentence = Sentence(
                    example=sentence_response,
                    from_api=True,
                    word_id=word.id
                )
                sentence.save()

                return raw_sentence_response["example"][0]

            else:
                return random.choice(word.sentence)

        words = Word.query.order_by(func.random()).limit(64)
        random_words = []

        for word in words:
            sentence = find_sentence(word)
            random_words.append({ "word": word.word[:-1], "sentence": sentence })

        return jsonify(random_words)

    @app.route('/login')
    def login():
        email = str(request.json.get('email', ''))
        password = str(request.json.get('password', ''))

        user = User.query.filter_by(email=email)[0]
        if user and bcrypt.check_password_hash(user.password_digest, password):
            response = jsonify({ "token": user.token })
            response.status_code = 303
            return response

    @app.route('/ideas', methods=['POST', 'DELETE'])
    def ideas():
        if request.method == "POST":
            token = str(request.json.get('id', ''))
            user = User.query.filter_by(token=token)
            action = Action.query.filter_by(action=str(request.json.get('action', '')))
            idea = Idea.query.filter_by(response=str(request.json.get('idea', '')))
            categories = request.json.get('categories', '')

            if str(request.json.get('isGenuis', '')) == 'True':
                is_genius = True
            if str(request.json.get('isGenuis', '')) == 'False':
                is_genius = False

            if user.count() <= 0:
                return make_response(jsonify(error="User not found."), 404)
            elif idea.count() > 0:
                return make_response(jsonify(error="{0} idea already exists in the database for {1} {2}.".format(action[0].action, user[0].first_name, user[0].last_name)), 400)
            else:
                idea = Idea(
                    response=str(request.json.get('idea', '')),
                    random_word=str(request.json.get('random_word', '')),
                    user_id=user[0].id,
                    action_id=action[0].id,
                    is_genius=is_genius,
                    question=str(request.json.get('question', ''))
                )
                idea.save()

                for category in categories:
                    found_cat = Category.query.filter_by(name=category['name'])
                    if found_cat.count() > 0:
                        new_idea_categories = idea_categories.insert().values(idea_id=idea.id, category_id=found_cat[0].id)
                        db.session.execute(new_idea_categories)
                        db.session.commit()
                    else:
                        new_category = Category(name=category['name'], user_id=user[0].id)
                        new_category.save()
                        new_idea_categories = idea_categories.insert().values(idea_id=idea.id, category_id=new_category.id)
                        db.session.execute(new_idea_categories)
                        db.session.commit()

                return make_response(jsonify(success="{0} idea for {1} {2} has been successfully created!".format(action[0].action, user[0].first_name, user[0].last_name)), 200)
        else:
            # add logic for deleting an idea here
            return jsonify(message='This is a DELETE request')

        return jsonify(message='Success')

    @app.route('/actions', methods=['POST'])
    def create_action():
        token = str(request.json.get('token', ''))
        action = str(request.json.get('action', ''))
        user = User.query.filter_by(token=token)

        if user.count() > 0:
            if Action.query.filter_by(action=action).count() == 0:
                action = Action(action=action, user_id=user[0].id)
                action.save()
                obj = {
                    'id': action.id,
                    'action': action.action,
                    'user_id': action.user_id
                }
                response = jsonify(obj)
                response.status_code = 201
                return response
            else:
                abort(make_response(jsonify(message="You already have that action!"), 404))
        else:
            abort(make_response(jsonify(message="Invalid user token."), 404))

    return app
