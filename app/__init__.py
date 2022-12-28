import os
from typing import Tuple
from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

from .views.web import index, heartbeat


def create(options: dict) -> Tuple[Flask, SQLAlchemy]:
    app = Flask(__name__)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=options['DATABASE_URI'],
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    app.add_url_rule('/heartbeat', view_func=heartbeat, methods=['GET'])

    app.add_url_rule('/', view_func=index, defaults={'path': ''}, methods=['GET'])
    app.add_url_rule('/<path:path>', view_func=index, methods=['GET'])

    return app, SQLAlchemy(app)

load_dotenv()
app, sqla = create(os.environ)
