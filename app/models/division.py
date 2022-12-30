from app.sqla import sqla


class Division(sqla.Model):
    __tablename__ = 'divisions'

    id = sqla.Column('id', sqla.Integer, primary_key=True)
    name = sqla.Column('name', sqla.String(100), nullable=False)
    conference_id = sqla.Column('conference_id', sqla.Integer, sqla.ForeignKey('conferences.id'), nullable=False)

    def __repr__(self):
        return f'<Division {self.name}>'
