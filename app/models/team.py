from app.sqla import sqla


class Team(sqla.Model):
    __tablename__ = 'teams'

    id = sqla.Column('id', sqla.Integer, primary_key=True)
    location = sqla.Column('location', sqla.String(100), nullable=True)
    nickname = sqla.Column('nickname', sqla.String(50), nullable=True)

    league_id = sqla.Column('league_id', sqla.String(10), sqla.ForeignKey('leagues.id'), nullable=False)
    conference_id = sqla.Column('conference_id', sqla.Integer, sqla.ForeignKey('conferences.id'), nullable=True)
    division_id = sqla.Column('division_id', sqla.Integer, sqla.ForeignKey('divisions.id'), nullable=True)

    def __repr__(self):
        return f'<Team {self.location} {self.nickname}>'
