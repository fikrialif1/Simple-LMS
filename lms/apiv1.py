from ninja import NinjaAPI
from ninja.errors import HttpError
from ninja.pagination import paginate
from typing import List

from ninja_jwt.authentication import JWTAuth

from .models import User, Course, Category
from .auth.schemas import CourseIn, CourseOut, DetailCourseOut
from .auth.permissions import is_instructor, is_admin
from .auth.auth_api import router as auth_router
from .models import Enrollment
from .auth.schemas import EnrollmentIn
from .auth.permissions import is_student
from .models import Progress, Lesson
from .auth.schemas import ProgressSchema

apiv1 = NinjaAPI(
    title="Simple LMS API",
    version="1.0.0",
)

jwt_auth = JWTAuth()

apiv1.add_router(
    "/auth/",
    auth_router
)



# LIST COURSES
@apiv1.get(
    "/courses/",
    response=List[CourseOut],
    tags=["Courses"]
)
@paginate
def listCourses(request, title: str = None):

    courses = Course.objects.for_listing()

    if title:
        courses = courses.filter(
            title__icontains=title
        )

    return courses


# DETAIL COURSE
@apiv1.get(
    "/courses/{id}",
    response=DetailCourseOut,
    tags=["Courses"]
)
def detailCourse(request, id: int):

    try:
        return Course.objects.get(pk=id)

    except Course.DoesNotExist:
        raise HttpError(
            404,
            "Course tidak ditemukan"
        )


# CREATE COURSE
@apiv1.post(
    "/courses/",
    response={201: CourseOut},
    auth=jwt_auth,
    tags=["Courses"]
)
def createCourse(request, data: CourseIn):

    is_instructor(request.user)

    category = Category.objects.first()

    if not category:
        raise HttpError(
            400,
            "Category belum ada"
        )

    course = Course.objects.create(
        title=data.title,
        instructor=request.user,
        category=category
    )

    return 201, course


# UPDATE COURSE
@apiv1.patch(
    "/courses/{id}",
    response=CourseOut,
    auth=jwt_auth,
    tags=["Courses"]
)
def updateCourse(request, id: int, data: CourseIn):

    is_instructor(request.user)

    try:
        course = Course.objects.get(pk=id)

    except Course.DoesNotExist:
        raise HttpError(
            404,
            "Course tidak ditemukan"
        )

    if course.instructor != request.user:
        raise HttpError(
            403,
            "Anda bukan pemilik course ini"
        )

    for attr, value in data.dict().items():
        setattr(course, attr, value)

    course.save()

    return course


# DELETE COURSE
@apiv1.delete(
    "/courses/{id}",
    response={204: None},
    auth=jwt_auth,
    tags=["Courses"]
)
def deleteCourse(request, id: int):

    is_admin(request.user)

    try:
        course = Course.objects.get(pk=id)

    except Course.DoesNotExist:
        raise HttpError(
            404,
            "Course tidak ditemukan"
        )

    course.delete()

    return 204, None


# ENROLL COURSE
@apiv1.post(
    "/enrollments",
    auth=jwt_auth,
    tags=["Enrollments"]
)
def enroll_course(request, data: EnrollmentIn):

    is_student(request.user)

    if Enrollment.objects.filter(
        student=request.user,
        course_id=data.course_id
    ).exists():

        raise HttpError(
            400,
            "Sudah terdaftar"
        )

    enrollment = Enrollment.objects.create(
        student=request.user,
        course_id=data.course_id
    )

    return {
        "id": enrollment.id,
        "message": "Berhasil enroll"
    }


# MY COURSES
@apiv1.get(
    "/enrollments/my-courses",
    auth=jwt_auth,
    tags=["Enrollments"]
)
def my_courses(request):

    is_student(request.user)

    enrollments = (
        Enrollment.objects
        .for_student_dashboard()
        .filter(student=request.user)
    )

    return [
        {
            "course_id": e.course.id,
            "title": e.course.title
        }
        for e in enrollments
    ]


# MARK PROGRESS
@apiv1.post(
    "/enrollments/{id}/progress",
    auth=jwt_auth,
    tags=["Enrollments"]
)
def mark_progress(request, id: int, data: ProgressSchema):

    is_student(request.user)

    try:
        enrollment = Enrollment.objects.get(pk=id)

    except Enrollment.DoesNotExist:
        raise HttpError(
            404,
            "Enrollment tidak ditemukan"
        )

    if enrollment.student != request.user:
        raise HttpError(
            403,
            "Bukan enrollment milik Anda"
        )

    try:
        lesson = Lesson.objects.get(
            pk=data.lesson_id
        )

    except Lesson.DoesNotExist:
        raise HttpError(
            404,
            "Lesson tidak ditemukan"
        )

    progress, created = (
        Progress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson
        )
    )

    progress.completed = True
    progress.save()

    return {
        "message": "Lesson selesai"
    }