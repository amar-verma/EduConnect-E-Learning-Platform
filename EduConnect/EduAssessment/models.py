from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.utils.timezone import now


class Form(models.Model):  
    course = models.ForeignKey('Course_Module.Course', on_delete=models.CASCADE, related_name="forms_course")  # Each form belongs to a course
    title = models.CharField(max_length=255)
    num_questions = models.IntegerField(default=0)  # Auto-updated based on the number of questions
    total_score = models.IntegerField(default=0)  # Auto-updated from question marks
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    num_responses = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    event_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)  # Automatically set when the object is created
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.course.title})"

class Question(models.Model):  
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name="questions")  # Link to the form
    question_text = models.CharField(max_length=500)
    question_type = models.CharField(
        max_length=20,
        choices=[
            ('mcq', 'Multiple Choice'), 
            ('checkbox', 'Checkbox'), 
            ('text', 'Text Answer')
        ]
    )
    options = models.JSONField(blank=True, default=list)  # Store multiple choices if needed
    answer_key = models.JSONField(blank=True, default=list)  # Store correct answers
    marks = models.IntegerField(default=1)  # Score for this question

    def __str__(self):
        return self.question_text

class StudentResponse(models.Model):  
    student = models.ForeignKey('Students.Student', on_delete=models.CASCADE)
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name="responses")  # Link response to form
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="responses")
    selected_answer = models.JSONField(blank=True, default=list)  # Student's selected options
    time_taken = models.IntegerField()  # Time taken in seconds
    submitted_at = models.DateTimeField(auto_now_add=True,null=True)
    score = models.IntegerField(default=0)  # Score for this question

    def __str__(self):
        return f"Response by {self.student} for {self.question}"
    

class FormAccessControl(models.Model):
    student = models.ForeignKey('Students.Student', on_delete=models.CASCADE)
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    has_access = models.BooleanField(default=False)  # Checkbox toggle for student access

    def __str__(self):
        return f"{self.student.first_name} - {self.form.title} ({'Allowed' if self.has_access else 'Restricted'})"
    





class Enrollment(models.Model):
    student = models.ForeignKey('Students.Student', on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey('Course_Module.Course', on_delete=models.CASCADE, related_name="enrolled_students")
    enrollment_date = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("Active", "Active"),
            ("Completed", "Completed"),
            ("Dropped", "Dropped")
        ],
        default="Active"
    )

    def __str__(self):
        return f"{self.student.first_name} enrolled in {self.course}"
    
    def course_end_date(self):
        return self.enrollment_date + timedelta(days=self.course.months * 30)
    
    def check_course_time(self):
        if timezone.now() > self.course_end_date():
            CourseTime.objects.create(enrollment=self, exceeded_at=timezone.now())
            return True
        return False
    
    def remaining_time_in_days(self):
        remaining_time = self.course_end_date() - timezone.now().date()
        return remaining_time.days if remaining_time.days > 0 else 0  

    def remaining_time_in_months(self):
        remaining_time_in_days = self.remaining_time_in_days()
        remaining_months = remaining_time_in_days // 30  
        return remaining_months if remaining_months > 0 else 0
    
class CourseTime(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    exceeded_at = models.DateTimeField() 
    status = models.CharField(
        max_length=20,
        choices=[
            ("Pending", "Pending"),
            ("Completed", "Completed"),
        ],
        default="Pending"
    )
    
    def __str__(self):
        return f"Course {self.enrollment.course.title} exceeded at {self.exceeded_at}"


class Message(models.Model):
    teacher = models.ForeignKey("Teachers.Teacher", on_delete=models.CASCADE)
    student = models.ForeignKey("Students.Student", on_delete=models.CASCADE)
    course = models.ForeignKey("Course_Module.Course", on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(default=now)
    is_read = models.BooleanField(default=False)  # Track if the message is read

    def __str__(self):
        return f"{self.teacher} -> {self.student}: {self.message[:30]}..."