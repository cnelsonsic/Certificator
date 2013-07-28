from .db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    full_name = db.Column(db.String(120))

    results = db.relationship("Result")

    def __init__(self, email, full_name=None):
        self.email = email
        if self.full_name:
            self.full_name = full_name

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

    certificate = db.relationship("Certificate", uselist=False, backref="result")

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

class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gid = db.Column(db.String, unique=True)
    purchased = db.Column(db.Boolean)
    date_purchased = db.Column(db.DateTime)

    result_id = db.Column(db.Integer, db.ForeignKey('result.id'))

    @staticmethod
    def rand_guid(length=8, seed=None):
        import random
        if seed:
            random.seed(seed)

        consonants = "bcdfghjklmnpqrstvwxz"
        return ''.join([random.choice(consonants) for _ in xrange(length)])

    def __init__(self, result, purchased=False, date_purchased=None):
        self.result = result

        # Loop until we get a unique guid.
        while True:
            self.gid = self.rand_guid()
            dupe = Certificate.query.filter_by(gid=self.gid).first()
            if not dupe:
                break
            else:
                continue

        self.purchased = purchased
        if purchased:
            if date_purchased:
                self.date_purchased = date_purchased
            else:
                self.date_purchased = datetime.datetime.now()
