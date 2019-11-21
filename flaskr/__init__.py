import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import MetaData

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    SQLALCHEMY_DATABASE_URI='sqlite:///{}/../database/depot.db'.format(basedir),
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
db = SQLAlchemy(app, metadata=MetaData(naming_convention=naming_convention))
migrate = Migrate(app, db, render_as_batch=True)

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
