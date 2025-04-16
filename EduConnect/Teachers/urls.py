from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.tech_home,name='tech_home'),
    path('login/',views.tech_login,name='tech_login'),
    path('dashboard/overview/',views.tech_overview,name='tech_overview'),
    path('dashboard/earning/',views.tech_earning,name='tech_earning'),
    path('course/my-course/',views.tech_mycourse,name='tech_mycourse'),
    path('course/<int:course_id>/', views.tech_course_detail, name='tech_course_detail'),
    # path('course/create-course/',views.tech_create_course,name='tech_create_course'),
    path('certification/issue/',views.tech_certificate,name='tech_certifiacte'),
    path('teacher/issue_certificate/', views.issue_certificate, name='issue_certificate'),
    path('certification/grade/',views.tech_grade,name='tech_grade'),
    path('update_course_status/', views.update_course_status, name='update_course_status'),
    path('communication/message/',views.tech_message,name='tech_message'),
    path('communication/announcement/',views.tech_emails,name='tech_emails'),
    path('communication/meeting/',views.tech_meeting,name='tech_meeting'),
    path("toggle_webinar_status/<int:webinar_id>/", views.toggle_webinar_status, name="toggle_webinar_status"),
    path('payment/receieve/',views.tech_rpay,name='tech_rpay'),
    path('discussion/student-queries/',views.tech_quries,name='tech_quries'),
    path('answer_query/<int:query_id>/', views.answer_query, name="answer_query"),
    path('discussion/forums/',views.tech_forums,name='tech_forums'),
    path('create_post/', views.create_post, name="create_post"),
    path('add_comment/<int:post_id>/', views.add_comment, name="add_comment"),
    path("delete_post/<int:post_id>/", views.delete_post, name="delete_post"),
    path('discussion/student-review/',views.tech_review,name='tech_review'),
    path('setting/',views.tech_setting,name='tech_setting'),
    path('setting/notification/update',views.update_teacher_notifications,name='update_teacher_notifications'),
    path("payments/<int:payment_id>/pay/", views.mark_payment_paid, name="mark_payment_paid"),
    path("update-teacher-profile/", views.update_teacher_profile, name="update_teacher_profile"),
    path("submit-feedback/", views.submit_teacher_feedback, name="tech_submit_feedback"),
    path('download-teacher/<int:teacher_id>/', views.generate_teacher_pdf, name='download_teacher_pdf'),
    path('verify/otp/',views.verify_otp_teacher,name='verify_otp_teacher'),
    path('verify/otp/resend/',views.resend_otp_teacher,name='resend_otp_teacher'),
    path('profile/setup/<str:username>',views.tech_reprofile,name='tech_reprofile'),
    path('profile/reset-password/',views.forget_password_teacher,name='forget_password_teacher'),
    path('profile/set-password/confirm/',views.tech_reset_password, name='tech_reset_password'),

    
    # path('get-course-content/<int:course_id>/', views.get_course_content, name='get_course_content'),
    # path('delete-assignment/<int:assignment_id>/', views.delete_assignment, name="delete_assignment"),
    # path('update-content/<int:content_id>/', views.update_content, name="update_content"),
    # path('get-content-details/<int:content_id>',views.get_content_details,name='get_content_details')

    # path('create-course/', views.tech_create_course, name='tech_create_course'),
    # path('api/create-course/', views.create_course, name='create_course_api'),
    # path('api/content/',views.create_content,name='create_content'),
    # path('api/course-content/<int:course_id>/', views.get_course_content, name='get_course_content'),
    # path('api/content/<int:content_id>/', views.update_content, name='update_content'),
    # path('api/content/<int:content_id>/delete/', views.delete_content, name='delete_content'),
    # path('edit-course/<int:course_id>/', views.edit_course, name='edit_course'),

    # path('course/create/', views.create_course, name='create_course'),
    # path('course/update/<int:course_id>/', views.update_course, name='update_course'),




    path('create/', views.create_course_z, name='create_course_z'),
    path('update-course/<int:course_id>/', views.update_course_z, name='update_course_z'),
    path('tech/assignments/', views.tech_assignments, name='tech_assignments'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root= settings.MEDIA_ROOT)