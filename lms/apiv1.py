from ninja import NinjaAPI
from ninja.errors import HttpError
from django.contrib.auth.models import User
from .models import Course
from .schemas import CourseIn, CourseOut, DetailCourseOut
from typing import List

apiv1 = NinjaAPI(
    title="Simple LMS API",
    version="1.0.0",
)

@apiv1.get('/courses/', response=List[CourseOut])
def listCourses(request):
    return Course.objects.all()


@apiv1.get('/courses/{id}', response=DetailCourseOut)
def detailCourse(request, id: int):
    try:
        return Course.objects.get(pk=id)
    except Course.DoesNotExist:
        raise HttpError(404, "Course tidak ditemukan")


@apiv1.post('/courses/', response={201: CourseOut})
def createCourse(request, data: CourseIn):
    instructor = User.objects.first()
    category = Category.objects.first()

    if not instructor or not category:
        raise HttpError(400, "Instructor atau Category belum ada")

    course = Course.objects.create(
        title=data.title,
        instructor=instructor,
        category=category
    )

    return 201, course


@apiv1.put('/courses/{id}', response=CourseOut)
def updateCourse(request, id: int, data: CourseIn):
    try:
        course = Course.objects.get(pk=id)
    except Course.DoesNotExist:
        raise HttpError(404, "Course tidak ditemukan")

    for attr, value in data.dict().items():
        setattr(course, attr, value)
    course.save()

    return course


@apiv1.delete('/courses/{id}', response={204: None})
def deleteCourse(request, id: int):
    try:
        course = Course.objects.get(pk=id)
    except Course.DoesNotExist:
        raise HttpError(404, "Course tidak ditemukan")

    course.delete()
    return 204, None