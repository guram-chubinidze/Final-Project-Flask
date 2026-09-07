from flask import Config, Flask
from flask_login import LoginManager
from models import db
from flask_bcrypt import Bcrypt


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)