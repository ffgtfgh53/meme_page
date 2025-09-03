from flask import Flask
from flask_login import LoginManager

from .extensions import db

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile("config.py")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    db.init_app(app)

    from .meme_page import app as main_blueprint
    app.register_blueprint(main_blueprint)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    from .account import account as account_blueprint
    app.register_blueprint(account_blueprint)
    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app=app)

    from .models import Users
    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))

    return app
    
with create_app().app_context():
    db.create_all()
    #creates database if does not exist