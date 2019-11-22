from flaskr import db


class Transaction(db.Model):
    """ Database table that stores transactions """
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(13), unique=True)
    stock_name = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    WKN = db.Column(db.String(6), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    provision = db.Column(db.Float, nullable=False)
    dividend_tax = db.Column(db.Float)
    church_tax = db.Column(db.Float)
    soli_tax = db.Column(db.Float)
    total = db.Column(db.Float, nullable=False)
    courtage = db.Column(db.Float)
    exchange_provision = db.Column(db.Float)
    due_date = db.Column(db.Date)
    closed = db.Column(db.SmallInteger)
    users = db.relationship('User', backref='transaction', lazy='dynamic')


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'))
    ratio = db.Column(db.Float, nullable=False)