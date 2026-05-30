from pydantic import BaseModel


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