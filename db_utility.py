"""Database utility functions for managing user data and course progress."""

from __init__ import db
from models import CourseDetails, CurrentPath, User


def get_current_path_details(username: str) -> CurrentPath | None:
    """Get user's current navigation path."""
    return CurrentPath.query.filter_by(username=username).first()


def get_current_course_details(
    username: str,
    last_visited_course: str,
) -> CourseDetails | None:
    """Get user's progress in a specific course."""
    return CourseDetails.query.filter_by(
        username=username,
        last_visited_course=last_visited_course,
    ).first()


def commit_current_course_details(
    username: str,
    last_visited_course: str,
    last_visited_topic: str,
    last_visited_index: int,
) -> None:
    """Save user's progress in a course."""
    current_course_details = CourseDetails(
        username=username,
        last_visited_course=last_visited_course,
        last_visited_topic=last_visited_topic,
        last_visited_index=last_visited_index,
    )
    db.session.merge(current_course_details)
    db.session.commit()


def commit_current_path_details(
    username: str,
    last_visited_directory: str,
    last_visited_course: str,
) -> None:
    """Save user's current navigation path."""
    current_path_details = CurrentPath(
        username=username,
        last_visited_directory=last_visited_directory,
        last_visited_course=last_visited_course,
    )
    db.session.merge(current_path_details)
    db.session.commit()


def get_current_user_details(username: str) -> User | None:
    """Get user details by username."""
    return User.query.filter_by(username=username).first()


def commit_current_user_details(current_user: User) -> None:
    """Save updated user details."""
    db.session.merge(current_user)
    db.session.commit()
