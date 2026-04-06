from django.contrib import admin
from .models import User, Category, Course, Lesson, Enrollment, Progress


# LESSON INLINE (PENTING)
class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1


# COURSE ADMIN
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'category')
    search_fields = ('title',)
    list_filter = ('category', 'instructor')

    inlines = [LessonInline]


# USER ADMIN
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'is_staff')
    list_filter = ('role',)

# CATEGORY ADMIN
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)

# ENROLLMENT ADMIN
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course')
    search_fields = ('student__username',)


# PROGRESS ADMIN
@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'lesson', 'completed')
    list_filter = ('completed',)