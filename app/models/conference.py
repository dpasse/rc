from app.sqla import sqla


class Conference(sqla.Model):
    __tablename__ = 'conferences'

    id = sqla.Column('id', sqla.Integer, primary_key=True)
    name = sqla.Column('name', sqla.String(100), nullable=False)
    league_id = sqla.Column('league_id', sqla.String(10), sqla.ForeignKey('leagues.id'), nullable=False)

    divisions = sqla.relationship('Division', backref='divisions')

    def __repr__(self):
        return f'<Conference {self.name}>'
