from django.urls import path
from . import views

urlpatterns = [
    # path("course/meeting/<str:meeting_id>/",views.meeting_videocall, name="meeting_videocall"),
    path('course/meeting/teacher/<str:meeting_id>/<int:course_id>/<int:webinar_id>/', views.teacher_join_meeting, name='teacher_meeting'),
    path('course/meeting/student/<str:meeting_id>/<int:course_id>/<int:webinar_id>/', views.student_join_meeting, name='student_meeting'),
    path('record-attendance/', views.record_attendance, name='record_attendance'),
]