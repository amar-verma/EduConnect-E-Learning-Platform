from django.contrib import admin
from .models import Form,StudentResponse,Question,Enrollment,FormAccessControl,CourseTime,Message
# Register your models here.
admin.site.register(Form)
admin.site.register(StudentResponse)
admin.site.register(Question)
admin.site.register(Enrollment)
admin.site.register(FormAccessControl)
admin.site.register(CourseTime)
admin.site.register(Message)