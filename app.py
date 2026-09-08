import os

from flask import Flask, abort, current_app, flash, jsonify, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from sqlalchemy import func, or_
from werkzeug.utils import secure_filename
from forms import LoginForm, ProfileForm, RecipeForm, RegisterForm
from models import Ingredient, Recipe, User, db
from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash
from config import Config
import logging
from logging.handlers import RotatingFileHandler

from utils import get_recipe_nutrition



app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

if not app.debug:
    file_handler = RotatingFileHandler('app.log', maxBytes=1024 * 1024, backupCount=3)
    file_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))
    file_handler.setLevel(logging.INFO)
    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('RecipeHub startup')

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# 1 & 14. მთავარი გვერდი - რეცეპტების სია თარიღის მიხედვით (ქარდ ფორმატში)
@app.route('/')
def index():
    title = "RecipeHub - Discover Delicious Recipes"
    category_filter = request.args.get('category','').strip()
    search_query = request.args.get('search','').strip().lower()
    
    query = Recipe.query.order_by(Recipe.created_at.desc())
    
    categories = ['breakfast', 'lunch', 'dinner', 'dessert', 'vegan']
    
    if search_query:
        query = query.filter(
            or_(
                Recipe.title.ilike(f'%{search_query}%'),
                Recipe.full_recipe.ilike(f'%{search_query}%')
            )
        )
    
    if category_filter:
        query = query.filter_by(category=category_filter).order_by(Recipe.created_at.desc())
    
        
    recipes = query.all()
    return render_template('index.html',title=title,
                           recipes=recipes, 
                           categories=categories,
                           current_search=search_query,
                           current_category=category_filter)

# 3. About გვერდი
@app.route('/about')
def about():
    title = "About - RecipeHub"
    return render_template('about.html', title=title)

# 1. რეგისტრაცია
@app.route('/register', methods=['GET', 'POST'])
def register():
    title = "Register - RecipeHub"
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pwd = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, email=form.email.data, gender=form.gender.data, password_hash=hashed_pwd)
        db.session.add(new_user)
        db.session.commit()
        # 1. წარმატებული ავტორიზაცია
        app.logger.info(f"Successful registration for user: {new_user.email}")
        flash('რეგისტრაცია წარმატებით დასრულდა! გთხოვთ გაიაროთ ავტორიზაცია.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form, title=title)

# 2. ავტორიზაცია
@app.route('/login', methods=['GET', 'POST'])
def login():
    title = "Login - RecipeHub"
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            # 1. წარმატებული ავტორიზაცია
            app.logger.info(f"Successful login for user: {user.email}")
            return redirect(url_for('index'))
        # 1. წარმატებული ავტორიზაცია
        app.logger.info(f"Failed login attempt for user: {form.email.data}")
        flash('არასწორი ელ.ფოსტა ან/და პაროლი.', 'danger')
    return render_template('login.html', form=form, title=title)

# Logout
@app.route('/logout')
@login_required
def logout():
    app.logger.info(f"User logged out: {current_user.email}")
    logout_user()    
    return redirect(url_for('index'))

# 5 & 12. ახალი რეცეპტის დამატება (CSRF-ით)
@app.route('/recipe/add', methods=['GET', 'POST'])
@login_required
def add_recipe():
    title = "Add Recipe - RecipeHub"
    extra_css = ["https://cdn.jsdelivr.net/npm/quill@2.0.3/dist/quill.snow.css"]
    
    extra_js = [ 
                url_for('static', filename='js/ingredients.js'),
                "https://cdn.jsdelivr.net/npm/quill@2.0.3/dist/quill.js",              
                url_for('static', filename='js/recipe_form.js')]
    
    form = RecipeForm(request.form)
    if form.validate_on_submit():
        recipe = Recipe(
            title=form.title.data,
            category=form.category.data,
            prep_time=form.prep_time.data,
            servings=form.servings.data,
            image_url=form.image_url.data,
            youtube_url=form.youtube_url.data,
            short_desc=form.short_desc.data,
            full_recipe=form.full_recipe.data,
            user_id=current_user.id
        )
        db.session.add(recipe)
        db.session.flush()
        
        for ing_data in form.ingredients.data:
            if ing_data['name'] and ing_data['amount']: # ვამოწმებთ, რომ ცარიელი არ იყოს
                new_ingredient = Ingredient(
                    name=ing_data.get('name'),
                    amount=ing_data.get('amount'),
                    recipe_id=recipe.id
                )
                db.session.add(new_ingredient)
        db.session.commit()
        app.logger.info(f"New recipe added by user {current_user.email}: {recipe.title}")
        flash('რეცეპტი წარმატებით დაემატა!', 'success')
        return redirect(url_for('index'))   
    
    return render_template('add.html', form=form, title=title, extra_css=extra_css, extra_js=extra_js)

# 7 & 16. რეცეპტის დეტალები და გარე API დინამიური მონაცემები
@app.route('/recipe/<int:recipe_id>')
def recipe_details(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    categories_with_counts = db.session.query(
        Recipe.category, 
        func.count(Recipe.id)
    ).filter(Recipe.category != None).group_by(Recipe.category).all()
    
    nutrition_data = get_recipe_nutrition(recipe.title)
    return render_template('details.html', recipe=recipe, nutrition=nutrition_data, categories_with_counts=categories_with_counts)

# 8. საკუთარი რეცეპტის რედაქტირება
@app.route('/recipe/<int:recipe_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    title = "Edit Recipe - RecipeHub"
    extra_css = ["https://cdn.jsdelivr.net/npm/quill@2.0.3/dist/quill.snow.css"]
        
    extra_js = [ 
                    url_for('static', filename='js/ingredients.js'),
                    "https://cdn.jsdelivr.net/npm/quill@2.0.3/dist/quill.js",              
                    url_for('static', filename='js/recipe_form.js')]
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.author_user != current_user:
        abort(403)
    form = RecipeForm(obj=recipe)
   
    if form.validate_on_submit():
        form.populate_obj(recipe)
        db.session.commit()        
        app.logger.info(f"Recipe updated by user: {current_user.email}")
        flash('რეცეპტი განახლდა!', 'success')
        return redirect(url_for('recipe_details', recipe_id=recipe.id))
    return render_template('add.html', form=form, edit_mode=True, title=title,recipe=recipe, extra_css=extra_css, extra_js=extra_js)

# 8. საკუთარი რეცეპტის წაშლა
@app.route('/recipe/<int:recipe_id>/delete', methods=['DELETE'])
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.author_user != current_user:
        abort(403)
    if request.method == 'DELETE':
        try:
          db.session.delete(recipe)
          db.session.commit()
          app.logger.info(f"Recipe deleted by user: {current_user.email}")
          flash(f'რეცეპტი {recipe.title} წაშლილია.', 'info')
          return jsonify({"status": "success", 'redirect_url': url_for('profile')}), 204  # Return a 204 No Content response for AJAX requests 
        except Exception as e:
                db.session.rollback()
                app.logger.error(f"Error occurred while deleting recipe: {e}")
                flash(f"ჩანაწერის წაშლა ვერ მოხერხდა! {e}","danger")
                return jsonify({"status": "error"})  
    else:
        app.logger.warning(f"Invalid request method for deleting recipe by user: {current_user.email}")
        flash("მეთოდი არ არის დაშვებული!","danger")
        return jsonify({"status": "error"})



# 13. პროფილი (მონაცემების რედაქტირებით)
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    title = "Profile - RecipeHub"
    extra_js = [url_for('static', filename='js/delete_conf.js')]
    recipes = Recipe.query.filter_by(user_id=current_user.id).all()
    form = ProfileForm(obj=current_user)
    
    if request.method == 'POST':
       
        if form.validate_on_submit():
            current_user.username = form.username.data
            current_user.email = form.email.data
            current_user.gender = form.gender.data
            # 2. სურათის ატვირთვის დამუშავება
            file = request.files.get('profile_image')
            if file and file.filename != '':
              filename = secure_filename(file.filename)
              # ვინახავთ static/images/ ფოლდერში
              upload_folder = os.path.join(current_app.root_path, 'static', 'images')
        
            
              file_path = os.path.join(upload_folder, filename)
              file.save(file_path)
              # ვწერთ ბაზაში ფაილის სახელს
              current_user.profile_image = filename
            
            db.session.commit()
            app.logger.info(f"Profile updated for user: {current_user.email}")
            flash('პროფილი განახლდა!', 'success')
            return redirect(url_for('profile'))
    return render_template('profile.html', form=form, title=title, recipes=recipes,extra_js=extra_js)

@app.route('/user/<int:user_id>/recipes')
def user_recipes(user_id):
    # ვეძებთ მომხმარებელს, თუ არ არსებობს - აგდებს 404 ერორს
    profile_user = User.query.get_or_404(user_id)
    
    # ვფილტრავთ და ვიღებთ მხოლოდ ამ მომხმარებლის რეცეპტებს
    recipes = Recipe.query.filter_by(user_id=profile_user.id).all()
    
    # ვამოწმებთ, საკუთარ პროფილზეა თუ არა შემოსული მიმდინარე მომხმარებელი
    is_owner = current_user.is_authenticated and current_user.id == profile_user.id
    
    return render_template('index.html', profile_user=profile_user, recipes=recipes, is_owner=is_owner)

# 11. Error Handlers: 404 & 500
@app.errorhandler(404)
def page_not_found(e):
    title = "404 Not Found - RecipeHub"
    return render_template('errors/404.html', title=title), 404

@app.errorhandler(403)
def forbidden(e):
    title = "403 Forbidden - RecipeHub"
    return render_template('errors/403.html', title=title), 403

@app.errorhandler(500)
def internal_server_error(e):
    title = "500 Internal Server Error - RecipeHub"
    return render_template('errors/500.html', title=title), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)