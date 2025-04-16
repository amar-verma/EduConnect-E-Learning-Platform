from django.db import models
from Edu_Main.models import User
from django.utils.timezone import now
# from Course_Module.models import Assignment,Content,Course,Webinar

#============================================================================
#Student
#============================================================================
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student',null=True,blank=True,unique=True)
    student_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    # username = models.CharField(max_length=50,null=True,blank=True,unique=True)
    # email = models.EmailField(unique=True,null=True)
    # password_hash = models.CharField(max_length=255)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")], null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    zip_code = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)

    enrollment_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    current_level = models.CharField(max_length=50, null=True, blank=True)
    program = models.CharField(max_length=100, null=True, blank=True)
    joining_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[("Active", "Active"), ("Inactive", "Inactive"), ("Suspended", "Suspended")], default="Active")

    bio = models.TextField(null=True, blank=True)
    social_links = models.JSONField(null=True, blank=True)  # For storing social media links
    preferences = models.JSONField(null=True, blank=True)  # For learning preferences
    notifications_enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)
    premium = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user.email})"
    




#============================================================================
#StudentProfile
#============================================================================
class StudentProfile(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    interests = models.JSONField(null=True, blank=True)  # Example: ["Programming", "Art"]
    skills = models.JSONField(null=True, blank=True)  # Example: ["Python", "Data Analysis"]
    achievements = models.JSONField(null=True, blank=True)  # Example: ["Hackathon Winner 2023"]
    bio = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Profile of {self.student.first_name} {self.student.last_name}"
    



class StudentNotificationSettings(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name="std_notification_settings")
    email_notifications = models.BooleanField(default=True)
    deletion_notifications = models.BooleanField(default=False)
    mobile_notifications = models.BooleanField(default=False)
    auth_notifications = models.BooleanField(default=False)
    course_notifications = models.BooleanField(default=False)


class StudentFeedback(models.Model):
    CATEGORY_CHOICES = [
        ("Course Content Quality", "Course Content Quality"),
        ("Instructor Performance", "Instructor Performance"),
        ("Platform Usability", "Platform Usability"),
        ("Live Session Experience", "Live Session Experience"),
        ("Assignment/Task Relevance", "Assignment/Task Relevance"),
        ("Certification Process", "Certification Process"),
        ("Support/Customer Service", "Support/Customer Service"),
        ("Payment Issues", "Payment Issues"),
        ("Other", "Other"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE,related_name='student_system_feedback' )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    custom_category = models.CharField(max_length=255, blank=True, null=True)
    feedback_text = models.TextField()
    rating = models.IntegerField()
    suggestions = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="feedback_uploads/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.student.first_name} - {self.category}"

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    payment_id = models.CharField(max_length=100)  # Unique Razorpay payment ID
    order_id = models.CharField(max_length=100)  # Unique Razorpay order ID
    student = models.ForeignKey(Student, on_delete=models.CASCADE,related_name='std_payment_id') 
    course = models.ForeignKey('Course_Module.Course', on_delete=models.CASCADE,related_name='course_payment_id') 
    amount = models.PositiveIntegerField(help_text="rupees") 
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 
    payment_method = models.CharField(max_length=50, blank=True, null=True) 
    payment_signature = models.CharField(max_length=255, blank=True, null=True) 
    
    def __str__(self):
        return f"Payment {self.payment_id} for {self.student.user.first_name} - {self.course.title}"



class StudentNotificationDashboard(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE ,related_name='notify_by_teacher')
    message = models.TextField()
    created_at = models.DateTimeField(default=now)
    is_read = models.BooleanField(default=False)  # Track if the notification is read
    
    def __str__(self):
        return f"Notification for {self.student.user.first_name}: {self.message[:30]}..."

class TeacherNotificationDashBoard(models.Model):
    teacher = models.ForeignKey('Teachers.Teacher', on_delete=models.CASCADE,related_name='notify_by_student')
    message = models.TextField()
    created_at = models.DateTimeField(default=now)
    is_read = models.BooleanField(default=False)  # Track if the notification is read
    
    def __str__(self):
        return f"Notification for {self.teacher.user.first_name}: {self.message[:30]}..."
    
class UserCalendarEvent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    event_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.first_name}'s event: {self.title}"
    
    
    
class SearchQuery(models.Model):
    query = models.CharField(max_length=255)
    count = models.PositiveIntegerField(default=1)
    last_searched = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.query} ({self.count})"
    
    class Meta:
        ordering = ['-count']