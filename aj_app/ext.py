from flask_bootstrap import Bootstrap
from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()


def init_ext(app):
    db.init_app(app)
    migrate.init_app(app=app, db=db)
    Bootstrap(app)
    # DebugToolbarExtension(app)
