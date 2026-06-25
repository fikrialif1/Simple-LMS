from celery import shared_task
from .models import Course
import csv

@shared_task
def test_task():
    print("Test task")

@shared_task
def send_enrollment_email(email, course_title):
    print(
        f"{email} enrolled in {course_title}"
    )

@shared_task
def generate_certificate(
    student_id,
    course_id
):
    print(
        f"Certificate generated "
        f"for student {student_id} "
        f"course {course_id}"
    )


@shared_task
def update_course_statistics():
    from .models import Course

    for course in Course.objects.all():

        total = course.enrollments.count()

        print(
            f"{course.title}: {total}"
        )

@shared_task
def export_course_report():
    with open("course_report.csv", "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow(["Course", "Students"])

        for course in Course.objects.all():
            writer.writerow([
                course.title,
                course.enrollments.count()
            ])

    print("Course report generated")