from app import db
from sqlalchemy.dialects.postgresql import JSON

class Person(db.Model):
    __tablename__ = 'people'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    messages = db.relationship('Message', backref='owner')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<id {}, name {}>'.format(self.id, self.name)

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    string = db.Column(db.String())
    owner_id = db.Column(db.Integer, db.ForeignKey('people.id'))
