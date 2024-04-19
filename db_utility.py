from .models import CurrentPath, CourseDetails, User
from . import db


def get_current_path_details(username):
    return CurrentPath.query.filter_by(username=username).first()


def get_current_course_details(username, last_visited_course):
    return CourseDetails.query.filter_by(username=username,
                                         last_visited_course=last_visited_course).first()


def commit_current_course_details(username, last_visited_course, last_visited_topic, last_visited_index):
    current_course_details = CourseDetails(username=username,
                                           last_visited_course=last_visited_course,
                                           last_visited_topic=last_visited_topic,
                                           last_visited_index=last_visited_index)
    db.session.merge(current_course_details)
    db.session.commit()


def commit_current_path_details(username, last_visited_directory, last_visited_course):
    current_path_details = CurrentPath(username=username, last_visited_directory=last_visited_directory,
                                       last_visited_course=last_visited_course)
    db.session.merge(current_path_details)
    db.session.commit()


def get_current_user_details(username):
    return User.query.filter_by(username=username).first()


def commit_current_user_details(current_user):
    db.session.merge(current_user)
    db.session.commit()
