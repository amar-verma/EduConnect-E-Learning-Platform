from django.db import models
from taggit.managers import TaggableManager
from django_ckeditor_5.fields import CKEditor5Field
from django.utils.timezone import now
import random
from django.utils import timezone


class Course(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    description2 = models.TextField(null=True, blank=True)
    teacher = models.ForeignKey('Teachers.Teacher', on_delete=models.CASCADE)  # Connects with the Teacher model
    duration = models.PositiveIntegerField(help_text="Duration in hours",default=24)
    course_img = models.ImageField(upload_to='course_images/', null=True, blank=True, default='default_images/default.png')
    category = models.CharField(max_length=100, choices=[
        ("Programming Language", "Programming Language"),
        ("Data Science", "Data Science"),
        ("Web Development", "Web Development"),
        ("Game Development", "Game Development"),
        ("Mobile Development", "Mobile Development"),
        ("Database Design", "Database Design"),
        ("Software Testing", "Software Testing"),
        ("Software Engineering", "Software Engineering"),
        ("Software Development Tools", "Software Development Tools"),
        ("No-Code Development", "No-Code Development"),
        ("Other", "Other"),
    ])
    old_price = models.PositiveIntegerField(help_text="old price",default=0)
    price = models.PositiveIntegerField(help_text="new price",default=0)
    tags = TaggableManager(blank=True)
    rating = models.PositiveIntegerField(help_text="rating 1 to 5",null=True,blank=True, default=1)
    enroll = models.PositiveIntegerField(help_text="no of student that have enroll",null=True, blank=True, default=0)
    max_enrollments = models.PositiveIntegerField(help_text="total no of student that can enroll",null=True, blank=True, default=100)
    like = models.PositiveIntegerField(help_text="no. of likes",default=0)
    dislike = models.PositiveIntegerField(help_text="no. of dislikes",default=0)
    is_display = models.BooleanField(default=False)
    is_content = models.BooleanField(default=False)
    is_data = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    meeting_code = models.CharField(max_length=10, blank=True,null=True)
    months = models.PositiveIntegerField(help_text="no. of months its take to complete course",default=3)

    def __str__(self):
        return self.title



class Content(models.Model):
    id = models.AutoField(primary_key=True)
    course_head = models.CharField(max_length=255, null=True, blank=True) 
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="content_items")
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    desc = CKEditor5Field(config_name='extends', null=True, blank=True)
    course_img = models.ImageField(upload_to='content_images/', null=True, blank=True)  # Optional image upload
    course_video = models.FileField(upload_to='content_videos/', null=True, blank=True)
    order = models.PositiveIntegerField(help_text="Order in the course module")
    is_mandatory = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} - {self.course.title}"
    

class CourseFeatures(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="content_features")
    features = models.TextField()
    def __str__(self):
        return f"{self.course}"

class CourseSkills(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="content_skills")
    skills = models.TextField()
    def __str__(self):
        return f"{self.course}"

class CourseLearning(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="content_learning")
    learn = models.TextField()
    def __str__(self):
        return f"{self.course}"

class CourseComment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="content_comment")
    name = models.CharField(max_length=255) 
    photo = models.ImageField(upload_to='course_comments/', null=True, blank=True, default='default_images/default.png')
    comment = models.TextField()
    value = models.BooleanField(default=False, help_text="Indicates whether the content is liked by the user")
    def __str__(self):
        return f"{self.course} - {self.name} " 


class EdUContent(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="edu_content")
    whoCan = models.TextField(null=True, blank=True)
    def __str__(self):
        return f"{self.course}"

class EduSupport(models.Model):
    name = models.CharField(max_length=200)
    mail_id = models.EmailField()
    from_pg = models.CharField(max_length=200)
    num = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.from_pg} - {self.mail_id}"
    

class Advertisement(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField(null=True, blank=True)  # Content or script for the ad
    image = models.ImageField(upload_to='ads/', null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    link = models.URLField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
class AdvertisementSmall(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField(null=True, blank=True)  # Content or script for the ad
    image = models.ImageField(upload_to='ads/', null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    link = models.URLField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
class AdsPic(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='ads/', null=True, blank=True)
    link = models.URLField(null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.title

class EduForm(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True,help_text="background")
    mail_id = models.EmailField()
    m_no = models.PositiveIntegerField(help_text="mobile number")

    def __str__(self):
        return f"{self.m_no} - {self.mail_id}"


class EduFeed(models.Model):
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='edufeed/', null=True, blank=True)
    description = models.TextField(null=True, blank=True,help_text="background")

    def __str__(self):
        return self.title


class EduOTP(models.Model):
    email = models.EmailField(help_text="This is the email") 
    otp = models.PositiveIntegerField(help_text="OTP")
    timestamp = models.DateTimeField(auto_now_add=True)  # Store OTP generation time
    is_verified = models.BooleanField(default=False)  # Mark OTP as used

    def is_expired(self):
        return (now() - self.timestamp).total_seconds() > 300  # Check if 5 min passed

    def __str__(self):
        return f"{self.email} - {self.otp} - {self.is_verified}"


class Assignment(models.Model):
    question = models.ForeignKey(Content, on_delete=models.CASCADE, related_name="content_assignment")
    title = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.question.title}"
    

class AssignmentSubmission(models.Model):
    student = models.ForeignKey('Students.Student', on_delete=models.CASCADE, related_name="student_submission")
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="on_submission")
    file = models.FileField(upload_to="assignment_submissions/", null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10,choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('rework', 'Rework')
        ],
        default='pending',  
    )
    message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.first_name} submitted {self.assignment.title}"


class StudentProgress(models.Model):
    student = models.ForeignKey('Students.Student', on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    assignment_submitted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('student', 'content')  # Ensures one entry per student-content pair

    def __str__(self):
        return f"{self.student.user.email} - {self.content.title} - Completed: {self.is_completed}"


class Certificate(models.Model):
    student = models.ForeignKey('Students.Student', on_delete=models.CASCADE, related_name="student_certifiacte")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="course_cetificate")
    created_at = models.DateTimeField(auto_now_add=True)









