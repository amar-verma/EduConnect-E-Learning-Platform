from django.contrib import admin
from .models import Teacher, TeacherCourse,TeacherAward, TeacherDashboard, TeacherFeedback, TeacherNotification, TeacherPerformance, TeacherProfile, TeacherSchedule,TeacherStudentData,ReceivedPayment,PaidPayment,StudentQuery,Post,Comment,TeacherNotificationSettings
# Register your models here.
from .models import TeacherPayment
admin.site.register(Teacher)
admin.site.register(TeacherProfile)
admin.site.register(TeacherCourse)
admin.site.register(TeacherStudentData)
admin.site.register(TeacherPerformance)
admin.site.register(TeacherDashboard)
admin.site.register(TeacherSchedule)
admin.site.register(TeacherNotification)
admin.site.register(TeacherFeedback)
admin.site.register(TeacherAward)
admin.site.register(ReceivedPayment)
admin.site.register(PaidPayment)
admin.site.register(StudentQuery)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(TeacherNotificationSettings)
admin.site.register(TeacherPayment)

