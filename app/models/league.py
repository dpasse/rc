from app.sqla import sqla


class League(sqla.Model):
    __tablename__ = 'leagues'

    id = sqla.Column('id', sqla.String(10), primary_key=True)
    name = sqla.Column('name', sqla.String(100), nullable=False)

    teams = sqla.relationship('Team', backref='leagues')
    conferences = sqla.relationship('Conference', backref='conferences')

    def __repr__(self):
        return f'<League {self.id}>'
