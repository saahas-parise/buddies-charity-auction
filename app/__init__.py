from flask import Flask
from flask_login import LoginManager
from .config import Config
from .db import DB
from flask_bootstrap import Bootstrap5

login = LoginManager()
login.login_view = 'users.login' 


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.db = DB(app)
    login.init_app(app)

    from .index import bp as index_bp
    app.register_blueprint(index_bp)

    from .users import bp as user_bp 
    app.register_blueprint(user_bp)
    
    from .purchased import bp as purchased_bp #copy and paste these two lines and change to purchased
    app.register_blueprint(purchased_bp)
    from .products import bp as product_bp
    app.register_blueprint(product_bp)

    from .reviews import bp as reviews_bp
    app.register_blueprint(reviews_bp)


    from .cart import bp as cart_bp
    app.register_blueprint(cart_bp)

    
    bootstrap = Bootstrap5(app)
    return app
#copy and paste index.py and change
#copy and paste index.html and change 
#copy and paste models/
