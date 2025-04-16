from django.urls import path
from . import views

urlpatterns = [
    # path('', views.test_index, name="test_index"),
    path('home/', views.test_home, name="test_home"),
    path("create-form/", views.create_form, name="create_form"),
    path('form/<int:form_id>/', views.test_form, name="test_form"),
    path("save-questions/<int:form_id>/", views.save_questions, name="save_questions"),
    path('form/<int:form_id>/view/', views.view_professor_form, name='view_professor_form'),
    path('form/<int:form_id>/responses/', views.view_student_responses, name='view_student_responses'),
    path('form/<int:form_id>/setting',views.form_settings_view,name="test_setting"),
    path('test/<int:form_id>/', views.student_take_test, name='student_take_test'),
    path('test/<int:form_id>/submit/', views.submit_student_test, name='submit_student_test'),

    # path("edit-questions/<int:form_id>/", views.edit_questions, name="edit_questions"),
    # path("edit-questions/<cid>/", views.edit_questions, name="edit_questions"),
    # path("update-questions/", views.update_questions, name="update_questions"),
]