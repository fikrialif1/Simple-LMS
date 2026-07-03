from pydantic import BaseModel
from ninja import Schema
from datetime import datetime
from typing import List
from ninja import Schema




# COURSE


class CourseOut(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True


class CourseIn(BaseModel):
    title: str


class DetailCourseOut(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True



# AUTH


class RegisterSchema(BaseModel):
    username: str
    email: str
    password: str
    role: str


class LoginSchema(BaseModel):
    username: str
    password: str


class UpdateProfileSchema(BaseModel):
    username: str | None = None
    email: str | None = None

class RefreshSchema(BaseModel):
    refresh: str



# ENROLLMENT


class EnrollmentIn(BaseModel):
    course_id: int


class ProgressSchema(BaseModel):
    lesson_id: int


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str

    class Config:
        from_attributes = True

# ANNOUNCEMENT

class AnnouncementIn(Schema):
    title: str
    content: str


class AnnouncementOut(Schema):
    id: int
    title: str
    content: str
    created_at: datetime


# STUDENT DASHBOARD
class StudentCourseProgressOut(Schema):
    course_id: int
    title: str
    progress_percentage: float
    completed: bool


class StudentDashboardOut(Schema):
    active_courses: int
    completed_courses: int
    courses: List[StudentCourseProgressOut]
    recommendations: List[str]


# INSTRUCTOR DASHBOARD
class StudentProgressOut(Schema):
    student: str
    course: str
    progress_percentage: float


class InstructorDashboardOut(Schema):
    total_courses: int
    total_enrollments: int
    most_popular_course: str | None
    student_progress: List[StudentProgressOut]

# HEALTH CHECK AND CHANGELOG
class HealthCheckOut(Schema):
    status: str
    database: str
    redis: str
    mongodb: str


class ChangelogOut(Schema):
    version: str
    changes: List[str]