import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    SQLALCHEMY_DATABASE_URI='sqlite:///{}/../database/depot.db'.format(basedir),
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from flaskr import models


# def create_app(test_config=None):
#     # create and configure app
#     app = Flask(__name__, instance_relative_config=True)
#     app.config.from_mapping(
#         SECRET_KEY='dev',
#         SQLALCHEMY_DATABASE_URI='sqlite:///../database/depot.db',
#         SQLALCHEMY_TRACK_MODIFICATIONS=False
#     )

#     db = SQLAlchemy(app)

#     if test_config is None:
#         app.config.from_pyfile('config.py', silent=True)
#     else:
#         app.config.from_mapping(test_config)

#     try:
#         os.makedirs(app.instance_path)
#     except OSError:
#         pass

#     print("test")

#     return app, db
