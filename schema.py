import graphene
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from app.models import *

class UserType(SQLAlchemyObjectType):

    class Meta:
        model = User

class ActionType(SQLAlchemyObjectType):

    class Meta:
        model = Action

class CategoryType(SQLAlchemyObjectType):

    class Meta:
        model = Category

class IdeaType(SQLAlchemyObjectType):

    class Meta:
        model = Idea

class Query(graphene.ObjectType):

    user = graphene.Field(UserType, id = graphene.Int())
    users = graphene.List(UserType, id = graphene.Int())

    def resolve_user(self, info, **kwargs):
        id = kwargs.get('id')
        return User.query.get(id)

    def resolve_users(self, info):        
        return User.query.all()

schema = graphene.Schema(query=Query)
