import enum
from sqlalchemy.orm import validates
from sqlalchemy import Column, Integer, String, Enum
from app.sqla import sqla


class Leagues(enum.Enum):
    nl = 1
    al = 2

class Team(sqla.Model):
    __tablename__ = 'teams'

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String, nullable=False)
    league = Column('league', Enum(Leagues), nullable=False)

    @validates('name', 'league')
    def not_empty(self, key: str, value: str) -> str:
        if not value:
            raise ValueError(f'{key.capitalize()} is required.')

        return value
