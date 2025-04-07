import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from redis import Redis
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address



db = SQLAlchemy()
migrate = Migrate()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

def create_app():
    load_dotenv()
    app = Flask(__name__)

    #Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost:5432/task_manager'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_POOL_SIZE'] = 10
    app.config['SQLALCHEMY_MAX_OVERFLOW'] = 20

    

    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app) 

    from .models import User, TaskManager, TaskLogger
    from .routes import main

    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    return app