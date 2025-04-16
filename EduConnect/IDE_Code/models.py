from django.db import models


# Create your models here.
class IdeData(models.Model):
    student = models.ForeignKey('Students.Student', on_delete=models.CASCADE, related_name="student_data")
    language = models.CharField(max_length=50) 
    title = models.TextField() 
    code = models.TextField()  
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return f"Code data for {self.student}"