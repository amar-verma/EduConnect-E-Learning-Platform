from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.home,name='home'),
    # path('javascript/', views.CourseDetail, name='CourseDetail'),
    path('why_us/', views.about_us, name='why_us'),
    path('join_us/', views.join_us, name='join_us'),
    path('teacher-profile/<int:teach_id>', views.teacher_profile, name='teacher_profile'),
    path('edu/<cname>', views.homeCard, name='homeCard'),
    path('course-detail/<int:course_id>/', views.course_detail, name='course_detail'),
    path('student-login/', views.std_login, name='std_login'),
    path('student-register/', views.std_register, name='std_register'),
    path('student-details-register/',views.std_register_next,name='std_register_next'),
    path('explore-courses/', views.explore_course, name='explore_course'),
    # path('student-register/otp/<int:no>', views.std_otp, name='std_otp'),
    path('filter_courses/', views.filter_courses, name='filter_courses'),
    path('course/<int:course_id>/',views.enroll_course, name='enroll_course'),
    path('course/<int:course_id>/content/<int:content_id>/', views.enroll_course_content, name='enroll_course_content'),
    path('course/submit-assignment/<int:assignment_id>/',views.submit_assignment,name='submit_assignment'),
    path("course/<int:course_id>/feedback/", views.course_feedback, name="course_feedback"),
    path('course/<int:course_id>/certificate/', views.enroll_certificate, name='enroll_certificate'),
    path('confirm-enrollment/<int:course_id>/', views.confirm_enrollment, name="confirm_enrollment"),
    path('course/payment-status/',views.payment_success,name='payment_success'),
    path('course/<int:course_id>/discussion/', views.enroll_post_std, name='enroll_post_std'),


    path('verify_login/',views.verify_student_login,name='verify_student_login'),
    path('verify-otp/', views.verify_otp,name='verify_otp'),
    path('resend_otp/',views.resend_otp,name='resend_otp'),
    path('forget-password/', views.std_forget_password, name='std_forget_password'),
    path('reset-password/', views.std_reset_password, name='std_reset_password'),

    path('search/', views.search_courses, name='search_courses'),
    path('search/clear-history/', views.clear_search_history, name='clear_search_history'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL,document_root= settings.MEDIA_ROOT)