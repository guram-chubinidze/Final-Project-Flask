from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone


db = SQLAlchemy()
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    gender = db.Column(db.String(1), nullable=False, default='f')  # 'm' for male, 'f' for female
    password_hash = db.Column(db.String(255), nullable=False)
    profile_image = db.Column(db.String(255), default="female.png")
    recipes = db.relationship('Recipe', backref='author_user', lazy=True)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    short_desc = db.Column(db.Text, nullable=False)
    full_recipe = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Breakfast, Lunch, Dinner, Dessert, Vegan...
    prep_time = db.Column(db.String(50), nullable=False)
    servings = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    youtube_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)   
    ingredients = db.relationship('Ingredient', backref='recipe', lazy=True, cascade="all, delete-orphan")
    
    @property
    def youtube_embed_url(self):
        if not self.youtube_url:
            return None
        
        url = self.youtube_url
        # თუ ბმულია ტიპის: https://www.youtube.com/watch?v=VIDEO_ID
        if 'watch?v=' in url:
            video_id = url.split('watch?v=')[1].split('&')[0]
            return f"https://www.youtube.com/embed/{video_id}"
        
        # თუ მოკლე ბმულია ტიპის: https://youtu.be/VIDEO_ID
        elif 'youtu.be/' in url:
            video_id = url.split('youtu.be/')[1].split('?')[0]
            return f"https://www.youtube.com/embed/{video_id}"
            
        elif 'embed/' in url:
            return url
            
        return None
    
    def __repr__(self):
        return f"Recipe('{self.title}', '{self.category}', '{self.created_at}')"


    
class Ingredient(db.Model):    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)       # მაგ: 'Lasagna noodles', 'Ground beef'
    amount = db.Column(db.String(50), nullable=False)     # მაგ: '1 box', '500g', '2 cups'
    
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    
    def __repr__(self):
        return f"Ingredient('{self.name}', '{self.amount}')"