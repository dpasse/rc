from flask_sqlalchemy import SQLAlchemy


def create_sqla():
    return SQLAlchemy()

sqla = create_sqla()
