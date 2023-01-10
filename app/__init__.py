import os
from typing import cast, Optional
from flask import Flask
from dotenv import load_dotenv
from app.sqla import sqla
from app.cache import cache
from app.views.web import web


basedir = os.path.abspath(os.path.dirname(__file__))

def create_app(config: Optional[dict] = None) -> Flask:
    rc_app = Flask(__name__)

    if not config:
        config = cast(dict, rc_app.env)

    rc_app.config.from_mapping(
        SECRET_KEY=config.get('FLASK_SECRET_KEY'),
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir, config.get('DATABASE') or ''),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ECHO=config.get('SQLALCHEMY_ECHO') == '1',
    )

    ## app.register_blueprint(api, url_prefix='/api')
    rc_app.register_blueprint(web)

    sqla.init_app(app=rc_app)
    cache.init_app(app=rc_app)

    return rc_app

load_dotenv()
app = create_app(cast(dict, os.environ))
