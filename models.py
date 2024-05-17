from datetime import datetime

from exts import db
from sqlalchemy.dialects.sqlite import JSON

# Dream model class
class DreamModel(db.Model):
    __tablename__ = 'dream'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    audio = db.Column(db.String(500), nullable=True)

    tag = db.Column(db.String(100), nullable=False)

    # create_time = db.Column(db.DateTime, default=datetime.now().replace(second=0, microsecond=0))
    run_time = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<Dream %r>' % self.title

