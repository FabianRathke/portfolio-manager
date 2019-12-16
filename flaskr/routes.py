from flask import render_template

from flaskr import app
from flaskr.models import Transactions


@app.route('/')
@app.route('/transactions')
def index():
    return render_template('transactions.html', transactions=Transactions.query.order_by('date').all())
