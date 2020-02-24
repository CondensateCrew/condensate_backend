from app import db, bcrypt
import secrets


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    password_digest = db.Column(db.String(255))
    token = db.Column(db.String(255))
    categories = db.relationship('Category', backref='user', lazy=True)
    actions = db.relationship('Action', backref='user', lazy=True)
    ideas = db.relationship('Idea', backref='user', lazy=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password_digest = bcrypt.generate_password_hash(password).decode('UTF-8')
        self.token = secrets.token_hex(16)

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return User.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    def __init__(self, name, user_id):
        self.name = name
        self.user_id = user_id

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Category.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return self.name


class Action(db.Model):
    __tablename__ = 'actions'

    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    def __init__(self, action, user_id):
        self.action = action
        self.user_id = user_id

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Action.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return self.action


idea_categories = db.Table('idea_categories',
    db.Column('idea_id', db.Integer, db.ForeignKey('ideas.id'), nullable=False, primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), nullable=False, primary_key=True)
)


class Idea(db.Model):
    __tablename__ = 'ideas'

    id = db.Column(db.Integer, primary_key=True)
    response = db.Column(db.Text)
    random_word = db.Column(db.String(255))
    question = db.Column(db.String(255))
    is_genius = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action_id = db.Column(db.Integer, db.ForeignKey('actions.id'), nullable=False)
    action = db.relationship('Action', backref='idea', lazy=True)
    categories = db.relationship('Category', secondary=idea_categories, lazy='subquery',
        backref=db.backref('ideas', lazy=True))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    def __init__(self,response, random_word, action_id, user_id, is_genius, question):
        self.response = response
        self.random_word = random_word
        self.is_genius = is_genius
        self.action_id = action_id
        self.user_id = user_id
        self.question = question

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Idea.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<Idea: {}>".format(self.response)

class Word(db.Model):
    __tablename__ = "words"

    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(255))

    def __init__(self, word):
        self.word = word

    def save(self):
        db.session.add(self)
        db.session.commit()

class Sentence(db.Model):
    __tablename__ = 'sentences'

    id = db.Column(db.Integer, primary_key=True)
    example = db.Column(db.Text)
    from_api = db.Column(db.Boolean)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)
    word = db.relationship('Word', backref='sentence', lazy=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    def __init__(self, example, from_api, word_id):
        self.example = example
        self.from_api = from_api
        self.word_id = word_id

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return self.example
