from app.sqla import sqla


class Team(sqla.Model):
    __tablename__ = 'teams'

    id = sqla.Column('id', sqla.Integer, primary_key=True)
    league = sqla.Column('league', sqla.String(10), sqla.ForeignKey('leagues.id'), nullable=False)
    location = sqla.Column('location', sqla.String(100), nullable=False)
    nickname = sqla.Column('nickname', sqla.String(50), nullable=False)

    def __repr__(self):
        return f'<Team {self.location} {self.nickname}>'
