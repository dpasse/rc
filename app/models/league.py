from app.sqla import sqla


class League(sqla.Model):
    __tablename__ = 'leagues'

    id = sqla.Column('id', sqla.String(10), primary_key=True)
    name = sqla.Column('name', sqla.String(100), nullable=False)
    parent_id = sqla.Column('parent_id', sqla.String(10), sqla.ForeignKey('leagues.id'), nullable=True)

    teams = sqla.relationship('Team', backref='leagues')

    def __repr__(self):
        return f'<League {self.id}>'
