from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('',views.std_home,name='std_home'),
    path('student_dashboard/',views.std_dashboard,name='std_dashboard'),
    path('student_profile/',views.std_profile,name='std_profile'),
    path('student_profile/edit/',views.std_profile_edit,name='std_profile_edit'),
    path('student_courses/',views.std_courses,name='std_courses'),
    path('student_events/',views.std_events,name='std_events'),
    path('student_achievement/',views.std_achievement,name='std_achievement'),
    path('student_pay/',views.std_pay,name='std_pay'),
    path('student_pay/details/<int:pay_id>/',views.std_payment,name='std_payment'),
    path('student_feedback/',views.std_feedback,name='std_feedback'),
    path('student_setting/',views.std_setting,name='std_setting'),
    path('download-invoice/<int:pay_id>/', views.generate_invoice_pdf, name='download_invoice'),
    path('api/calendar/events/', views.calendar_event_create, name='calendar_event_create'),
    path('download_payment_pdf/', views.download_payment_pdf, name='download_payment_pdf'),
    path('deactivate-account/', views.deactivate_account, name='deactivate_account'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root= settings.MEDIA_ROOT)