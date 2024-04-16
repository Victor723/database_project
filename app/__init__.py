from flask import Flask
from flask_login import LoginManager
from .config import Config
from .db import DB


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
    
    from .sellers import bp as seller_bp
    app.register_blueprint(seller_bp)

    from .carts import bp as carts_bp
    app.register_blueprint(carts_bp)

    from .myreview import bp as myreview_bp
    app.register_blueprint(myreview_bp)

    from .order_history import bp as order_history_bp
    app.register_blueprint(order_history_bp)

    from .product_details import bp as product_details_bp
    app.register_blueprint(product_details_bp)

    return app
