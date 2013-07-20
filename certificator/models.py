from .db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    results = db.relationship("Result")

    def __init__(self, email):
        self.email = email

    def __repr__(self):
        return '<User {}>'.format(self.email)

    def is_active(self):
        return True

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return True

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    testname = db.Column(db.String)
    percentage = db.Column(db.Float)
    dateadded = db.Column(db.DateTime)

    def __init__(self, user, testname, percentage, dateadded=None):
        if not dateadded:
            import datetime
            dateadded = datetime.datetime.now()
        if hasattr(user, 'email'):
            user = user.id
        self.user = user
        self.testname = testname
        self.percentage = percentage
        self.dateadded = dateadded

    def __repr__(self):
        return "<Result {self.testname} {self.percentage} {self.dateadded}".format(self=self)
