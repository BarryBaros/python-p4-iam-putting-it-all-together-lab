#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        image_url = data.get('image_url')
        bio = data.get('bio')

        if not username or not password:
            return {'error': 'Username and passworrd are requiered.'}, 422
        
        try:
            # instance to create new
            new_user = User(
                username=username,
                password_hash=password,
                image_url=image_url,
                bio=bio
            )

            # Add and commit new user to DB
            db.session.add(new_user)
            db.session.commit()

            # Save user id in session
            session['user_id'] = new_user.id

            # Return json response
            response = {
                'id': new_user.username,
                'username': new_user.username,
                'image_url': new_user.image_url,
                'bio': new_user.bio
            }
            return response, 201
        
        except IntegrityError as e:
            db.session.rollback()
            return {'error': 'A user with that username already exixsts.'}, 422
        except Exception as e:
            return {'error': str(e)}, 500
    pass

class CheckSession(Resource):
    pass

class Login(Resource):
    pass

class Logout(Resource):
    pass

class RecipeIndex(Resource):
    pass

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)