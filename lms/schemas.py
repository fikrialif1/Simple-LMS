from pydantic import BaseModel

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