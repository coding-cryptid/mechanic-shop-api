import os
from dotenv import load_dotenv
from flask import Flask
from .models import db
from .extensions import ma, limiter, cache
from .blueprints.customers import customers_bp
from .blueprints.service_tickets import service_tickets_bp
from .blueprints.mechanics import mechanics_bp
from .blueprints.inventory import inventory_bp
from app.blueprints.users import users_bp

load_dotenv()


def create_app(config_name="DevelopmentConfig"):
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    app.register_blueprint(customers_bp, url_prefix="/customers")
    app.register_blueprint(
        service_tickets_bp,
        url_prefix="/service_tickets",
    )
    app.register_blueprint(mechanics_bp, url_prefix="/mechanics")
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(users_bp, url_prefix='/users')

    return app