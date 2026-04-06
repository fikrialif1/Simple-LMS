from django.db import connection
from .models import Course

def show_queries():
    #  N+1 Problem
    connection.queries_log.clear()

    courses = Course.objects.all()
    for c in courses:
        print(c.instructor.username)

    print("N+1 Query Count:", len(connection.queries))

    #  Optimized
    connection.queries_log.clear()

    courses = Course.objects.for_listing()
    for c in courses:
        print(c.instructor.username)

    print("Optimized Query Count:", len(connection.queries))