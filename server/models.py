from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    # Establish a relationship with Recipe
    recipes = relationship('Recipe', backref='user', lazy=True)

    @hybrid_property
    def password_hash(self):
        raise Exception('Password hashes may not be viewed.')
    
    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(
            password.encode('utf-8')
        ).decode('utf-8')
        
    def authenticate(self, password):
        """
        Authenticate a user with a provided password.
        """
        return bcrypt.check_password_hash(
            self._password_hash,
            password.encode('utf-8')
        )

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer, nullable=False)

    # Use foreign key to link to user model
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    @validates('title')
    def validate_title(self, key, title):
        """
        Validate the title of the recipe.
        """
        if not title:
            raise ValueError("Title must be present.")
        return title
    
    @validates('instructions')
    def validate_instructions(self, key, instructions):
        """
        Validate the instructions for the recipe.
        """
        if len(instructions) < 50:
            raise ValueError("Instructions must be at least 50 characters long.")
        return instructions
    
    def __repr__(self):
        return f'Recipe {self.title} by User ID: {self.user_id}'
