from flask_login import UserMixin
from sqlalchemy import PrimaryKeyConstraint
from . import db


class User(UserMixin, db.Model):
    # primary keys are required by SQLAlchemy
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    username = db.Column(db.String(1000))
    downloadaccess = db.Column(db.Boolean)


class CourseDetails(db.Model):
    __tablename__ = 'coursedetails'
    username = db.Column(db.String(1000), primary_key=True)
    last_visited_course = db.Column(db.String(1000), primary_key=True)
    last_visited_topic = db.Column(db.String(1000))
    last_visited_index = db.Column(db.Integer)

    __table_args__ = (
        PrimaryKeyConstraint('username', 'last_visited_course'),
    )


class CurrentPath(db.Model):
    __tablename__ = 'currentpath'
    username = db.Column(db.String(1000), primary_key=True)
    last_visited_directory = db.Column(db.String(1000))
    last_visited_course = db.Column(db.String(1000))
