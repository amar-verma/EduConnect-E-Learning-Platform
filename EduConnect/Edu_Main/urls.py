from django.urls import path
from . import views

urlpatterns = [
    # path("course/meeting/<str:meeting_id>/",views.meeting_videocall, name="meeting_videocall"),
    path('',views.edu_payment,name='edu_payment'),
    path('edu_mail/', views.senduseremail, name='senduseremail'),
    path('api/chat/', views.chatbot_api, name='chatbot_api'), 
    path('save_chat_history/', views.save_chat_history, name='save_chat_history'),
    path('load_chat_history/', views.load_chat_history, name='load_chat_history'),
    path('logout/', views.user_logout, name='logout'),
    path('guidelines/', views.edu_rules, name='guidelines'),
]