from django.db import models

# Create your models here.
class Webinar(models.Model):
    course = models.ForeignKey("Course_Module.Course", on_delete=models.CASCADE, related_name="webinars")
    teacher = models.ForeignKey('Teachers.Teacher', on_delete=models.CASCADE,related_name="webinars_teacher") 
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    meeting_link = models.URLField(null=True, blank=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} - {self.course.title}"
    
class WebinarAttendance(models.Model):
    student = models.ForeignKey('Students.Student', on_delete=models.CASCADE, related_name="webinars_std_att")
    webinar = models.ForeignKey(Webinar, on_delete=models.CASCADE, related_name="webinars_std_id")
    attended = models.BooleanField(default=False)
    join_time = models.DateTimeField(null=True, blank=True)
    leave_time = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['student', 'webinar']

    def __str__(self):
        return f"{self.student} - {self.webinar}"