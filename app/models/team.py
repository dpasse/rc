from app import sqla
from sqlalchemy.orm import validates


class Team(sqla.Model):
    __tablename__ = 'teams'

    id = sqla.Column(sqla.Integer, primary_key=True)
    name = sqla.Column(sqla.Text, nullable=False)

    @validates('name')
    def not_empty(self, key: str, value: str) -> str:
        if not value:
            raise ValueError(f'{key.capitalize()} is required.')

        return value
