#!/usr/bin/env python3

from flask import request, session, jsonify
from flask_restful import Resource
from werkzeug.security import check_password_hash, generate_password_hash
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
                password_hash=generate_password_hash(password),
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


class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')

        if user_id:
            user = User.query.get(user_id)
            if user:
                response = {
                    'id': user.id,
                    'username': user.username,
                    'image_url': user.image_url,
                    'bio': user.bio
                }
                return response, 200
            else:
                return {'error': 'User not found in the database.'}, 401
        else:
            return {'error': 'User not logged in.'}, 401

class Login(Resource):
    def post():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return {'error': 'Username and password are required.'}, 400
        
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            response = {
                'id': user.id,
                'username': user.username,
                'image_url': user.image_url,
                'bio': user.bio
            }
            return response, 200
        else:
            return {'error': 'Invalid username or passowrd.'}, 401
    

class Logout(Resource):
    def delete(self):
        if 'user_id' in session:
            session.pop('user_id', None)
            return '', 204
        
        else:
            return {'error': 'User not logged in.'}, 401

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        
        if user_id:
            recipes = Recipe.query.all()
            recipe_list = [
                {
                    'id': recipe.id,
                    'title': recipe.title,
                    'instructions': recipe.instructions,
                    'minutes_to_complete': recipe.minutes_to_complete,
                    'user': {
                        'id': recipe.user.id,
                        'username': recipe.user.username,
                        'image_url': recipe.user.image_url,
                        'bio': recipe.user.bio
                    }
                }
                for recipe in recipes
            ]
            return recipe_list, 200  # Correct status code
        else:
            return {'error': 'User not logged in.'}, 401
        
    def post(self):
        user_id = session.get('user_id')
        
        if user_id:
            data = request.get_json()
            title = data.get('title')
            instructions = data.get('instructions')
            minutes_to_complete = data.get('minutes_to_complete')

            if not title or not instructions or minutes_to_complete is None:
                return {'error': 'Title, instructions, and minutes to complete are required.'}, 422

            try:
                new_recipe = Recipe(
                    title=title,
                    instructions=instructions,
                    minutes_to_complete=minutes_to_complete,
                    user_id=user_id
                )

                db.session.add(new_recipe)
                db.session.commit()

                response = {
                    'id': new_recipe.id,
                    'title': new_recipe.title,
                    'instructions': new_recipe.instructions,
                    'minutes_to_complete': new_recipe.minutes_to_complete,
                    'user': {
                        'id': new_recipe.user.id,
                        'username': new_recipe.user.username,
                        'image_url': new_recipe.user.image_url,
                        'bio': new_recipe.user.bio
                    }
                }
                return response, 201

            except Exception as e:
                db.session.rollback()
                return {'error': str(e)}, 500
        else:
            return {'error': 'User not logged in.'}, 401

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)