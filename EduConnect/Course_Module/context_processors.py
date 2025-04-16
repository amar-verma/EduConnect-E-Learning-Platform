# context_processors.py
import datetime
from datetime import datetime
from .models import Advertisement, Course, CourseComment

def navbar_courses(request):
    # Fetch courses for the navbar
    programming_course = Course.objects.filter(category='Programming Language',is_display=True, id__isnull=False).order_by('-rating')[:5]
    data_course = Course.objects.filter(category='Data Science',is_display=True, id__isnull=False).order_by('-rating')[:5]
    web_course = Course.objects.filter(category='Web Development',is_display=True, id__isnull=False).order_by('-rating')[:5]
    game_course = Course.objects.filter(category='Game Development',is_display=True, id__isnull=False).order_by('-rating')[:5]
    mobile_course = Course.objects.filter(category='Mobile Development',is_display=True, id__isnull=False).order_by('-rating')[:5]
    database_course = Course.objects.filter(category='Database Design',is_display=True, id__isnull=False).order_by('-rating')[:5]
    testing_course = Course.objects.filter(category='Software Testing',is_display=True, id__isnull=False).order_by('-rating')[:5]
    software_course = Course.objects.filter(category='Software Engineering',is_display=True, id__isnull=False).order_by('-rating')[:5]
    development_course = Course.objects.filter(category='Software Development Tools',is_display=True, id__isnull=False).order_by('-rating')[:5]
    no_course = Course.objects.filter(category='No-Code Development', id__isnull=False).order_by('-rating')[:5]
    other_course = Course.objects.filter(category='Other',is_display=True, id__isnull=False).order_by('-rating')[:5]
    return {
        'programming_course_edu': programming_course,
        'data_course_edu': data_course,
        'web_course_edu': web_course,
        'game_course_edu': game_course,
        'mobile_course_edu': mobile_course,
        'database_course_edu': database_course,
        'testing_course_edu': testing_course,
        'software_course_edu': software_course,
        'development_course_edu': development_course,
        'no_course_edu': no_course,
        'other_course_edu': other_course,

    }



def advertisment(request):
    ads = Advertisement.objects.filter(is_active=True, start_date__lte=datetime.now(), end_date__gte=datetime.now())[:1]
    return {'edu_ads': ads}


def course_rating(request):
    courses = Course.objects.all()
    for course in courses:
        likes = CourseComment.objects.filter(course=course, value=True).count()
        dislikes = CourseComment.objects.filter(course=course, value=False).count()
        course.like = likes
        course.dislike = dislikes
        total_feedback = likes + dislikes
        if total_feedback > 0:
            course.rating = max(1, round((likes * 5) / total_feedback, 2))
        else:
            course.rating = 1 
        
        course.save()
    return {'edu_courses_rating': courses}
