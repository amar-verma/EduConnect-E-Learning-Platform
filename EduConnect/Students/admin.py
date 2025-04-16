from django.contrib import admin
from .models import Student,StudentProfile,StudentNotificationSettings,StudentFeedback,Payment,StudentNotificationDashboard,TeacherNotificationDashBoard,UserCalendarEvent,SearchQuery
# Register your models here.

admin.site.register(Student)
admin.site.register(StudentProfile)
admin.site.register(StudentNotificationSettings)
admin.site.register(StudentFeedback)
admin.site.register(Payment)
admin.site.register(StudentNotificationDashboard)
admin.site.register(TeacherNotificationDashBoard)
admin.site.register(UserCalendarEvent)
admin.site.register(SearchQuery)


