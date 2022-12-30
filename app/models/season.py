from app.sqla import sqla


class Season(sqla.Model):
    __tablename__ = 'seasons'

    id = sqla.Column('id', sqla.String(10), primary_key=True)

    def __repr__(self):
        return f'<Season {self.id}>'
