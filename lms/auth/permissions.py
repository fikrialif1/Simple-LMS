from ..utils import api_error


def is_admin(user):
    if not user.is_superuser:
        api_error(403, "Admin only")


def is_instructor(user):
    if user.role != "instructor":
        api_error(403, "Instructor only")


def is_student(user):
    if user.role != "student":
        api_error(403, "Student only")