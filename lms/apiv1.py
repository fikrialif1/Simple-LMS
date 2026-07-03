from datetime import datetime
from typing import List

from django.core.cache import cache
from django.db import connection
from django.db.models import Count

from ninja import NinjaAPI
from ninja.pagination import paginate
from ninja_jwt.authentication import JWTAuth

from pymongo.errors import PyMongoError

from .auth.auth_api import router as auth_router
from .auth.permissions import (
    is_admin,
    is_instructor,
    is_student,
)
from .auth.schemas import (
    AnnouncementIn,
    AnnouncementOut,
    CourseIn,
    CourseOut,
    DetailCourseOut,
    EnrollmentIn,
    InstructorDashboardOut,
    ProgressSchema,
    StudentCourseProgressOut,
    StudentDashboardOut,
    StudentProgressOut,
)

from .models import (
    Announcement,
    Category,
    Course,
    Enrollment,
    Lesson,
    Progress,
    User,
)

from .mongo import db

from .tasks import (
    export_course_report,
    generate_certificate,
    send_enrollment_email,
)

from .utils import (
    api_error,
    api_success,
    http_error_handler,
)


apiv1 = NinjaAPI(
    title="Simple LMS API",
    version="1.0.0",
)

from ninja.errors import HttpError
from django.http import JsonResponse


@apiv1.exception_handler(HttpError)
def handle_http_error(request, exc):
    return http_error_handler(request, exc)

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

    cache_key = f"courses:{title}"

    cached = cache.get(cache_key)

    if cached:
        print("CACHE HIT")
        return cached

    print("CACHE MISS")

    courses = Course.objects.for_listing()

    if title:
        courses = courses.filter(
            title__icontains=title
        )

    result = list(courses)

    cache.set(
        cache_key,
        result,
        timeout=900
    )

    print("CACHE SAVED:", cache_key)

    return result


# DETAIL COURSE
@apiv1.get(
    "/courses/{id}",
    response={
        200: dict,
        404: dict
    },
    tags=["Courses"]
)
def detailCourse(request, id: int):

    cache_key = f"course:{id}"

    cached = cache.get(cache_key)

    if cached:
        return cached

    try:
        course = Course.objects.get(pk=id)

        response_data = api_success(
            "Detail course berhasil diambil",
            {
                "id": course.id,
                "title": course.title
            }
        )

        cache.set(
            cache_key,
            response_data,
            timeout=900
        )

        return response_data

    except Course.DoesNotExist:
        api_error(404, "Course tidak ditemukan")


# CREATE COURSE
@apiv1.post(
    "/courses/",
    response={
        201: dict,
        400: dict,
        403: dict
    },
    auth=jwt_auth,
    tags=["Courses"]
)
def createCourse(request, data: CourseIn):

    is_instructor(request.user)

    category = Category.objects.first()

    if not category:
        api_error(400, "Category belum ada")

    course = Course.objects.create(
        title=data.title,
        instructor=request.user,
        category=category
    )

    db.activity_logs.insert_one({
        "user_id": request.user.id,
        "course_id": course.id,
        "action": "create_course",
        "timestamp": datetime.utcnow()
    })

    cache.delete_pattern("courses:*")

    return 201, api_success(
        "Course berhasil dibuat",
        {
            "id": course.id,
            "title": course.title,
            "instructor": course.instructor.username
        }
    )


# UPDATE COURSE
@apiv1.patch(
    "/courses/{id}",
    response={
        200: dict,
        403: dict,
        404: dict
    },
    auth=jwt_auth,
    tags=["Courses"]
)
def updateCourse(request, id: int, data: CourseIn):

    is_instructor(request.user)

    try:
        course = Course.objects.get(pk=id)

    except Course.DoesNotExist:
        api_error(404, "Course tidak ditemukan")

    if course.instructor != request.user:
        api_error(403, "Anda bukan pemilik course ini")

    for attr, value in data.dict().items():
        setattr(course, attr, value)

    course.save()

    db.activity_logs.insert_one({
        "user_id": request.user.id,
        "course_id": course.id,
        "action": "update_course",
        "timestamp": datetime.utcnow()
    })

    cache.delete_pattern("courses:*")
    cache.delete(f"course:{course.id}")

    return api_success(
        "Course berhasil diperbarui",
        {
            "id": course.id,
            "title": course.title
        }
    )


# DELETE COURSE
@apiv1.delete(
    "/courses/{id}",
    response={
        200: dict,
        403: dict,
        404: dict
    },
    auth=jwt_auth,
    tags=["Courses"]
)
def deleteCourse(request, id: int):

    is_admin(request.user)

    try:
        course = Course.objects.get(pk=id)

    except Course.DoesNotExist:
        api_error(404, "Course tidak ditemukan")

    cache.delete_pattern("courses:*")
    cache.delete(f"course:{course.id}")

    db.activity_logs.insert_one({
        "user_id": request.user.id,
        "course_id": course.id,
        "action": "delete_course",
        "timestamp": datetime.utcnow()
    })

    course.delete()

    return api_success(
        "Course berhasil dihapus"
    )


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

       api_error(400, "Sudah terdaftar")

    enrollment = Enrollment.objects.create(
        student=request.user,
        course_id=data.course_id
    )

    db.activity_logs.insert_one({
        "user_id": request.user.id,
        "course_id": data.course_id,
        "action": "enroll_course",
        "timestamp": datetime.utcnow()
    })

    send_enrollment_email.delay(
        request.user.email,
        enrollment.course.title
    )

    return api_success(
        "Berhasil enroll course",
        {
            "enrollment_id": enrollment.id,
            "course": enrollment.course.title
        }
    )


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
    response={
        200: dict,
        403: dict,
        404: dict
    },
    auth=jwt_auth,
    tags=["Enrollments"]
)
def mark_progress(request, id: int, data: ProgressSchema):

    is_student(request.user)

    try:
        enrollment = Enrollment.objects.get(pk=id)

    except Enrollment.DoesNotExist:
        api_error(404, "Enrollment tidak ditemukan")

    if enrollment.student != request.user:
        api_error(403, "Bukan enrollment milik Anda")

    try:
        lesson = Lesson.objects.get(
            pk=data.lesson_id
        )

    except Lesson.DoesNotExist:
        api_error(404, "Lesson tidak ditemukan")

    progress, created = (
        Progress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson
        )
    )

    progress.completed = True
    progress.save()

    completed_lessons = Progress.objects.filter(
        enrollment=enrollment,
        completed=True
    ).count()

    total_lessons = Lesson.objects.filter(
        course=enrollment.course
    ).count()

    if total_lessons > 0 and completed_lessons == total_lessons:
        generate_certificate.delay(
            request.user.id,
            enrollment.course.id
        )

    db.learning_analytics.insert_one({
        "student_id": request.user.id,
        "course_id": enrollment.course.id,
        "lesson_id": lesson.id,
        "completed": True,
        "timestamp": datetime.utcnow()
    })

    return api_success(
        "Lesson selesai",
        {
            "lesson_id": lesson.id,
            "course": enrollment.course.title
        }
    )

# STUDENT DASHBOARD
@apiv1.get(
    "/dashboard/student",
    response={
        200: dict,
        403: dict
    },
    auth=jwt_auth,
    tags=["Dashboard"]
)
def student_dashboard(request):

    is_student(request.user)

    enrollments = (
        Enrollment.objects
        .select_related("course")
        .filter(student=request.user)
    )

    courses_data = []

    active_courses = 0
    completed_courses = 0

    for enrollment in enrollments:

        total_lessons = Lesson.objects.filter(
            course=enrollment.course
        ).count()

        completed_lessons = Progress.objects.filter(
            enrollment=enrollment,
            completed=True
        ).count()

        progress_percentage = 0

        if total_lessons > 0:
            progress_percentage = round(
                (completed_lessons / total_lessons) * 100,
                2
            )

        is_completed = (
            total_lessons > 0
            and completed_lessons == total_lessons
        )

        if is_completed:
            completed_courses += 1
        else:
            active_courses += 1

        courses_data.append({
            "course_id": enrollment.course.id,
            "title": enrollment.course.title,
            "progress_percentage": progress_percentage,
            "completed": is_completed
        })

    # rekomendasi sederhana:
    # tampilkan 3 course yang belum diambil student

    enrolled_ids = enrollments.values_list(
        "course_id",
        flat=True
    )

    recommendations = list(
        Course.objects.exclude(
            id__in=enrolled_ids
        ).values_list(
            "title",
            flat=True
        )[:3]
    )

    return api_success(
        "Dashboard berhasil diambil",
        {
            "active_courses": active_courses,
            "completed_courses": completed_courses,
            "courses": courses_data,
            "recommendations": recommendations
        }
    )

# INSTRUCTOR DASHBOARD
@apiv1.get(
    "/dashboard/instructor",
    response={
        200: dict,
        403: dict
    },
    auth=jwt_auth,
    tags=["Dashboard"]
)
def instructor_dashboard(request):

    is_instructor(request.user)

    courses = Course.objects.filter(
        instructor=request.user
    )

    total_courses = courses.count()

    total_enrollments = Enrollment.objects.filter(
        course__in=courses
    ).count()

    popular_course = (
    Course.objects
    .filter(instructor=request.user)
    .annotate(total=Count("enrollments")) 
    .order_by("-total")
    .first()
)

    student_progress = []

    enrollments = (
        Enrollment.objects
        .select_related("student", "course")
        .filter(course__in=courses)
    )

    for enrollment in enrollments:

        total_lessons = Lesson.objects.filter(
            course=enrollment.course
        ).count()

        completed_lessons = Progress.objects.filter(
            enrollment=enrollment,
            completed=True
        ).count()

        percentage = 0

        if total_lessons > 0:
            percentage = round(
                (completed_lessons / total_lessons) * 100,
                2
            )
        
        most_popular_course = (
            popular_course.title
            if popular_course
            else None
        )

        student_progress.append({
            "student": enrollment.student.username,
            "course": enrollment.course.title,
            "progress_percentage": percentage
        })

    return api_success(
        "Dashboard instructor berhasil diambil",
        {
            "total_courses": total_courses,
            "total_enrollments": total_enrollments,
            "most_popular_course": most_popular_course,
            "student_progress": student_progress
        }
    )


# ANALYTICS REPORT
@apiv1.get(
    "/reports/enrollments",
    tags=["Reports"]
)
def enrollment_report(request):

    result = list(
        db.activity_logs.aggregate([
            {
                "$group": {
                    "_id": "$course_id",
                    "total": {
                        "$sum": 1
                    }
                }
            }
        ])
    )

    for item in result:
        item["_id"] = str(item["_id"])

    return result

@apiv1.post(
    "/reports/export",
    auth=jwt_auth,
    tags=["Reports"]
)
def export_report(request):

    is_admin(request.user)

    export_course_report.delay()

    return api_success(
        "Export report sedang diproses"
    )

@apiv1.get(
    "/reports/analytics",
    auth=jwt_auth,
    tags=["Reports"]
)
def learning_analytics_report(request):

    is_admin(request.user)

    result = list(
        db.learning_analytics.aggregate([
            {
                "$group": {
                    "_id": "$course_id",
                    "completed_lessons": {
                        "$sum": 1
                    }
                }
            }
        ])
    )

    for item in result:
        item["_id"] = str(item["_id"])

    return api_success(
        "Analytics berhasil diambil",
        result
    )

# ANNOUNCEMENTS
@apiv1.post(
    "/courses/{course_id}/announcements",
    response={
        200: dict,
        403: dict,
        404: dict
    },
    auth=jwt_auth,
    tags=["Announcement"]
)
def create_announcement(request, course_id: int, data: AnnouncementIn):

    try:
        course = Course.objects.get(id=course_id)

    except Course.DoesNotExist:
        api_error(404, "Course tidak ditemukan")

    if request.user != course.instructor:
        api_error(403, "Only instructor can create announcements")

    announcement = Announcement.objects.create(
        course=course,
        title=data.title,
        content=data.content
    )

    return api_success(
        "Pengumuman berhasil dibuat",
        {
            "id": announcement.id,
            "title": announcement.title,
            "content": announcement.content,
            "created_at": announcement.created_at
        }
    )

@apiv1.get(
    "/courses/{course_id}/announcements",
    response=dict,
    auth=jwt_auth,
    tags=["Announcement"]
)
def list_announcements(request, course_id: int):

    announcements = Announcement.objects.filter(
        course_id=course_id
    )

    data = [
        {
            "id": a.id,
            "title": a.title,
            "content": a.content,
            "created_at": a.created_at
        }
        for a in announcements
    ]

    return api_success(
        "Daftar pengumuman berhasil diambil",
        data
    )

# HEALTH CHECK
@apiv1.get(
    "/health",
    response=dict,
    tags=["System"]
)
def health_check(request):

    # PostgreSQL
    try:
        connection.ensure_connection()
        db_status = "ok"
    except Exception:
        db_status = "error"

    # Redis
    try:
        cache.set("health_check", "ok", 10)
        cache.get("health_check")
        redis_status = "ok"
    except Exception:
        redis_status = "error"

    # MongoDB
    try:
        db.command("ping")
        mongo_status = "ok"
    except Exception:
        mongo_status = "error"

    return api_success(
        "Health check berhasil",
        {
            "status": "healthy",
            "database": db_status,
            "redis": redis_status,
            "mongodb": mongo_status
        }
    )

# API CHANGELOG
@apiv1.get(
    "/changelog",
    response=dict,
    tags=["System"]
)
def api_changelog(request):

    return api_success(
        "Daftar perubahan API",
        {
            "version": "v1.0.0",
            "changes": [
                "Authentication JWT",
                "CRUD Course",
                "Enrollment & Progress Tracking",
                "Course Announcement",
                "Student Dashboard",
                "Instructor Dashboard",
                "Consistent API Response & Error Format",
                "Health Check Endpoint",
                "API Changelog Endpoint",
                "Redis Caching",
                "MongoDB Analytics",
                "Celery Background Tasks"
            ]
        }
    )