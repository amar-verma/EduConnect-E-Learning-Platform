from django.contrib import admin
from .models import Content,Course,EdUContent,EduSupport,Advertisement,EduForm,EduFeed,CourseComment,CourseFeatures,CourseLearning,CourseSkills,AdvertisementSmall,AdsPic,Assignment,AssignmentSubmission,StudentProgress,Certificate
from .models import EduOTP
# Register your models here.

admin.site.register(Course)
admin.site.register(Content)
admin.site.register(Assignment)
admin.site.register(AssignmentSubmission)
admin.site.register(EdUContent)
admin.site.register(EduSupport)
admin.site.register(Advertisement)
admin.site.register(EduFeed)
admin.site.register(EduForm)
admin.site.register(CourseComment)
admin.site.register(CourseFeatures)
admin.site.register(CourseLearning)
admin.site.register(CourseSkills)
admin.site.register(AdvertisementSmall)
admin.site.register(AdsPic)
admin.site.register(EduOTP)
admin.site.register(Certificate)
admin.site.register(StudentProgress)