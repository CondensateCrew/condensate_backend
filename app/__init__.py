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
from flask_cors import CORS

def create_app(config_name):
    from app.models import User, Word, Sentence, Action, Idea, Category, idea_categories, user_actions

    app = Flask(__name__, instance_relative_config=True)
    CORS(app)
    app.config['JSON_SORT_KEYS'] = False
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.route('/users', methods=['POST'])
    def users():
        if request.method == "POST":
            first_name = str(request.json.get('first_name', ''))
            last_name = str(request.json.get('last_name', ''))
            email = str(request.json.get('email', ''))
            password = str(request.json.get('password', ''))
            actions = Action.query.all()
            categories = Category.query.all()

            if User.query.filter_by(email=email).count() > 0:
                abort(make_response(jsonify(message="A user with this email already exists."), 400))
            elif first_name and last_name and email and password:
                user = User(first_name=first_name, last_name=last_name, email=email, password=password)
                user.save()
                for action in actions:
                    user.actions.append(action)

                for category in categories:
                    user.categories.append(category)

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

    @app.route('/dashboard', methods=['POST'])
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

    @app.route('/seed')
    def nouns():
        file = open("nouns.txt", "r")
        word_count = 0
        for line in file:
            if Word.query.filter_by(word=line.rstrip()).count() == 0:
                dbWord = Word(word=line.rstrip())
                dbWord.save()
                word_count += 1

        file = open("actions.txt", "r")
        action_count = 0
        for line in file:
            if Action.query.filter_by(action=line.rstrip()).count() == 0:
                dbAction = Action(action=line.rstrip())
                dbAction.save()
                action_count += 1

        file = open("categories.txt", "r")
        category_count = 0
        for line in file:
            if Category.query.filter_by(name=line.rstrip()).count() == 0:
                dbCategory = Category(name=line.rstrip())
                dbCategory.save()
                category_count += 1

        return jsonify({"Words Added":word_count, "Actions Added":action_count, "Categories Added": category_count})

    @app.route('/game_setup', methods=['POST'])
    def setup():
        def find_sentence(word):
            if len(word.sentence) < 3:
                url = "https://twinword-word-graph-dictionary.p.rapidapi.com/example/"
                querystring = {"entry":word.word}
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

                return sentence.example

            else:
                return random.choice(word.sentence).example

        if not request.data:
            return make_response(jsonify(error="Missing token."), 400)

        token = str(request.json.get('token', ''))
        user = User.query.filter_by(token=token)

        if user.count() > 0:
            words = Word.query.order_by(func.random()).limit(64)
            random_words = []

            for word in words:
                sentence = find_sentence(word)
                random_words.append({ "word": word.word, "sentence": sentence })

            return jsonify(random_words)
        else:
            return make_response(jsonify(error="User not found."), 404)

    @app.route('/login', methods=['POST'])
    def login():
        email = str(request.json.get('email', ''))
        password = str(request.json.get('password', ''))

        user = User.query.filter_by(email=email)[0]
        if user and bcrypt.check_password_hash(user.password_digest, password):
            response = jsonify({ "token": user.token, "first_name": user.first_name, "last_name": user.last_name })
            response.status_code = 303
            return response

    @app.route('/ideas', methods=['POST', 'DELETE'])
    def ideas():
        if not request.data:
            return make_response(jsonify(error="Missing parameters."), 400)

        if request.method == "POST":
            token = str(request.json.get('id', ''))
            user = User.query.filter_by(token=token)
            action = Action.query.filter_by(action=str(request.json.get('action', '')))
            idea = Idea.query.filter_by(response=str(request.json.get('idea', '')))
            categories = request.json.get('categories', '')

            if str(request.json.get('isGenius', '')) == 'True':
                is_genius = True
            if str(request.json.get('isGenius', '')) == 'False':
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
                    new_idea_categories = idea_categories.insert().values(idea_id=idea.id, category_id=found_cat[0].id)
                    db.session.execute(new_idea_categories)
                    db.session.commit()

                return make_response(jsonify(success="{0} idea for {1} {2} has been successfully created!".format(action[0].action, user[0].first_name, user[0].last_name)), 200)

        if request.method == "DELETE":
            token = str(request.json.get('token', ''))
            user = User.query.filter_by(token=token)
            idea_id = str(request.json.get('idea_id', ''))

            if user.count() <= 0:
                return make_response(jsonify(error="User not found."), 404)
            else:
                idea = Idea.query.filter_by(id=idea_id, user_id=user[0].id)

                if idea.count() <= 0:
                    return make_response(jsonify(error="Idea not found."), 404)
                else:
                    idea_name = idea[0].question
                    Idea.delete(idea[0])
                    return make_response('', 204)


    @app.route('/actions', methods=['POST'])
    def create_action():
        token = str(request.json.get('token', ''))
        action = str(request.json.get('action', ''))
        user = User.query.filter_by(token=token)

        if user.count() > 0:
            if Action.query.filter_by(action=action).count() == 0:
                action = Action(action=action)
                action.save()
                obj = {
                    'id': action.id,
                    'action': action.action,
                }
                new_user_action = user_actions.insert().values(user_id=user[0].id, action_id=action.id)
                db.session.execute(new_user_action)
                db.session.commit()
                response = jsonify(obj)
                response.status_code = 201
                return response
            else:
                abort(make_response(jsonify(message="You already have that action!"), 404))
        else:
            abort(make_response(jsonify(message="Invalid user token."), 404))

    return app
