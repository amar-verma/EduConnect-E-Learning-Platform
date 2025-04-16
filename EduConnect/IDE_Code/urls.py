from django.urls import path
from . import views

urlpatterns = [
    
    path('',views.index, name='ide_index'),
    path('editor/', views.home, name='IDE_page_home'),
    path('editor/<int:id>/', views.home,name='IDE_page'),

    # path('save_snippet/', views.save_code_snippet, name='save_snippet'),
    # path('execute_code/', views.execute_code, name='execute_code'),
    path('submit_code/', views.submit_code, name='submit_code'),
]