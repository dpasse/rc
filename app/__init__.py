import os
from flask import Flask
from dotenv import load_dotenv
from app.sqla import sqla
from app.views.web import index, heartbeat


basedir = os.path.abspath(os.path.dirname(__file__))

def create_app(options: dict) -> Flask:
    app = Flask(__name__)

    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir, os.getenv('DATABASE')),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    app.add_url_rule('/heartbeat', view_func=heartbeat, methods=['GET'])

    app.add_url_rule('/', view_func=index, defaults={'path': ''}, methods=['GET'])
    app.add_url_rule('/<path:path>', view_func=index, methods=['GET'])

    sqla.init_app(app=app)

    return app

load_dotenv()
app = create_app(os.environ)
