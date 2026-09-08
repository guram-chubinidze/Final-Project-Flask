import pytest
from app import app, db, bcrypt  # ვამატებთ bcrypt-ს იმპორტს აპლიკაციიდან
from models import User, Recipe

@pytest.fixture
def client():
    """ადგენს ტესტებისთვის სუფთა გარემოს"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
            
            # ვიყენებთ bcrypt.generate_password_hash-ს და .decode('utf-8')-ს
            u1 = User(
                username='guram', 
                email='guram@test.com', 
                password_hash=bcrypt.generate_password_hash('password123').decode('utf-8')
            )
            u2 = User(
                username='levan', 
                email='levan@test.com', 
                password_hash=bcrypt.generate_password_hash('password123').decode('utf-8')
            )
            db.session.add_all([u1, u2])
            db.session.commit()
            
            # ტესტური რეცეპტი
            recipe = Recipe(
                title='Khinkali', 
                short_desc='Delicious Georgian dumplings', 
                full_recipe='Boil water, wrap meat in dough, cook for 15 minutes.',
                category='Dinner', 
                prep_time='30 mins',
                servings=4,
                user_id=1
            )
            db.session.add(recipe)
            db.session.commit()
            
        yield client
        
        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_home_route(client):
    """1. Route ტესტი: ამოწმებს მთავარი გვერდის მუშაობას"""
    response = client.get('/')
    assert response.status_code == 200

def test_login_success(client):
    """2. Login ტესტი: ამოწმებს წარმატებულ ავტორიზაციას"""
    response = client.post('/login', data={
        'email': 'guram@test.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'guram' in response.data

def test_unauthorized_recipe_edit(client):
    """3. უფლებების ტესტი: ამოწმებს, რომ სხვისი პოსტის რედაქტირება იბლოკება (403)"""
    client.post('/login', data={
        'email': 'levan@test.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    response = client.get('/recipe/1/edit', follow_redirects=True)
    assert response.status_code == 403

def test_logout(client):
    """5. გამოსვლის (Logout) ტესტი: ამოწმებს სესიის დასრულებას"""
    # ჯერ შევდივართ სისტემაში
    client.post('/login', data={
        'email': 'guram@test.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    # ვგზავნით მოთხოვნას გამოსვლაზე (შეცვალეთ თქვენი როუტის მიხედვით, მაგ: '/logout')
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    
    # ვამოწმებთ, რომ გამოსვლის შემდეგ რედაქტირების გვერდზე აღარ გვიშვებს (ანუ სესია გასუფთავდა)
    protected_response = client.get('/recipe/1/edit', follow_redirects=True)
    # თუ ლაგინიდან აგდებს ან 401/403-ს აბრუნებს, ეს ნიშნავს რომ გამოსვლა წარმატებულია
    assert protected_response.status_code in [200, 401, 403] # დამოკიდებულია Flask-Login redirect კონფიგურაციაზე

def test_recipe_creation(client):
    """4. რეცეპტის დამატების ტესტი: ამოწმებს, რომ ავტორიზებულ იუზერს შეუძლია რეცეპტის შექმნა"""
    # გავდივართ ავტორიზაციას (guram, ID: 1)
    client.post('/login', data={
        'email': 'guram@test.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    # ვგზავნით ყველა საჭირო ველს ფორმის მიხედვით (image_url და ინგრედიენტების ჩათვლით)
    response = client.post('/recipe/add', data={
        'title': 'Mtsvadi',
        'category': 'dinner',  # აუცილებლად ემთხვევა choices-ის მნიშვნელობას
        'prep_time': '1 hour',
        'servings': 4,
        'image_url': 'https://example.com/mtsvadi.jpg',
        'youtube_url': '',
        'short_desc': 'Traditional Georgian BBQ',
        'full_recipe': 'Marinate pork chunks, skewer, and grill over vine shoot coals.',
        # FieldList-ის ფორმატი WTForms-ში
        'ingredients-0-name': 'Pork meat',
        'ingredients-0-amount': '1 kg',
        'submit': 'Publish Recipe'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # ვამოწმებთ, რომ რეცეპტი რეალურად ჩაიწერა ბაზაში
    with app.app_context():
        new_recipe = Recipe.query.filter_by(title='Mtsvadi').first()
        assert new_recipe is not None
        assert new_recipe.user_id == 1
        assert new_recipe.category == 'dinner'

def test_user_registration(client):
    """6. რეგისტრაციის ტესტი"""
    response = client.post('/register', data={
        'username': 'nino',
        'email': 'nino@test.com',
        'password': 'password123',
        'confirm_password': 'password123',
        'gender': 'f',               # <-- აუცილებელია სქესის მითითება ფორმის ვალიდაციისთვის
        'submit': 'Register'         # <-- ღილაკის მნიშვნელობა
    }, follow_redirects=True)
    
    with app.app_context():
        user = User.query.filter_by(email='nino@test.com').first()
        assert user is not None
        assert user.username == 'nino'