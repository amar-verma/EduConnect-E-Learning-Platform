from django.db import models
from multiselectfield import MultiSelectField
from django.utils.timezone import now
from Edu_Main.models import User
# from Students.models import Student
# from Course_Module.models import Assignment,Content,Course,Webinar


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher',null=True,blank=True,unique=True)
    teacher_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    # email = models.EmailField(unique=True)
    # password_hash = models.CharField(max_length=255)
    profile_picture = models.ImageField(upload_to='teacher_images/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    social_links = models.TextField(null=True, blank=True)
    joining_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[("Active", "Active"), ("Inactive", "Inactive"), ("Suspended", "Suspended")], default="Active")

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user.email})"


class TeacherProfile(models.Model):
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE, related_name='profile')
    qualifications = models.TextField(null=True, blank=True)  # List of qualifications
    experience_years = models.PositiveIntegerField(null=True, blank=True)
    philosophy = models.TextField(null=True, blank=True) 
    specializations = models.TextField(null=True, blank=True)  # List of specializations
    languages_spoken = models.TextField(null=True, blank=True)  # List of languages
    interest = models.TextField(null=True, blank=True)
    AVAILABLE_DAYS = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    availability = MultiSelectField(choices=AVAILABLE_DAYS, blank=True, null=True)
    social_links_linkedin = models.TextField(null=True, blank=True)
    social_links_github = models.TextField(null=True, blank=True)
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    public_visibility = models.BooleanField(default=True)
    two_factor_auth = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile of {self.teacher}"
    
class TeacherAward(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="teacher_award")
    title = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='teacher_awards/', null=True, blank=True)



class ReceivedPayment(models.Model):
    student = models.ForeignKey('Students.Student', on_delete=models.CASCADE, related_name="payments_received")
    course = models.ForeignKey('Course_Module.Course', on_delete=models.CASCADE, related_name="course_payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField(help_text="Duration in months",null=True,blank=True)
    payment_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.first_name} - {self.course.title} - ${self.amount}"

class PaidPayment(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="payments_made")
    course = models.ForeignKey('Course_Module.Course', on_delete=models.CASCADE, related_name="teacher_payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Commission paid to EduConnect")
    payment_date = models.DateField(auto_now_add=True)
    desc = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.teacher.first_name} - {self.course.title} - ${self.amount}"


class StudentQuery(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
    ]

    student = models.ForeignKey('Students.Student', on_delete=models.CASCADE, related_name="student_queries")
    course = models.ForeignKey('Course_Module.Course', on_delete=models.CASCADE, related_name="course_queries")
    query_text = models.TextField()
    response_text = models.TextField(blank=True, null=True)  # Teacher's answer
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Query by {self.student.first_name} - {self.course.title}"

#to create a post
class Post(models.Model):
    teacher = models.ForeignKey('Teachers.Teacher', on_delete=models.CASCADE, related_name="posts")
    course = models.ForeignKey('Course_Module.Course', on_delete=models.CASCADE, related_name="course_posts")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.teacher.first_name} ({self.course.title})"

#store comment on post by teacher and student
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    student = models.ForeignKey('Students.Student', on_delete=models.CASCADE, null=True, blank=True)
    teacher = models.ForeignKey('Teachers.Teacher', on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.teacher:
            return f"Comment by {self.teacher.first_name} (Teacher)"
        elif self.student:
            return f"Comment by {self.student.first_name} (Student)"
        return "Unknown Comment"



class TeacherNotificationSettings(models.Model):
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE, related_name="notification_settings")
    email_notifications = models.BooleanField(default=True)
    deletion_notifications = models.BooleanField(default=False)
    mobile_notifications = models.BooleanField(default=False)
    auth_notifications = models.BooleanField(default=False)
    course_notifications = models.BooleanField(default=False)


class TeacherPayment(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="payments")
    title = models.CharField(max_length=255)  # Payment title from EduConnect
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount payable
    created_date = models.DateTimeField(auto_now_add=True)  # When EduConnect generated it

    description = models.TextField(blank=True, null=True)  # Optional teacher input
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("paid", "Paid")],
        default="pending"
    )
    update_date = models.DateTimeField(blank=True, null=True)  # When teacher makes payment

    def mark_as_paid(self):
        """Marks payment as paid with timestamp."""
        self.status = "paid"
        self.update_date = now()
        self.save()

    def __str__(self):
        return f"{self.teacher.first_name} - {self.title} - {self.amount} ({self.status})"


class TeacherFeedback(models.Model):
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

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    custom_category = models.CharField(max_length=255, blank=True, null=True)
    feedback_text = models.TextField()
    rating = models.IntegerField()
    suggestions = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="feedback_uploads/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.teacher.first_name} - {self.category}"







































class TeacherCourse(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teacher_courses')
    course = models.ForeignKey('Course_Module.Course', on_delete=models.CASCADE, related_name='teacher_courses')
    role = models.CharField(max_length=20, choices=[("Creator", "Creator"), ("Co-Teacher", "Co-Teacher")])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.teacher} - {self.course} ({self.role})"


class TeacherSchedule(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='schedules')
    activity_type = models.CharField(max_length=50, choices=[("Webinar", "Webinar"), ("Office Hour", "Office Hour"), ("Meeting", "Meeting")])
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.activity_type}: {self.title} ({self.teacher})"




class TeacherDashboard(models.Model):
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE, related_name='dashboard')
    total_courses = models.PositiveIntegerField(default=0)
    active_students = models.PositiveIntegerField(default=0)
    average_feedback_score = models.FloatField(default=0.0)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    last_login = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Dashboard of {self.teacher}"


class TeacherNotification(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.teacher}: {self.title}"


class TeacherPerformance(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='performances')
    month = models.DateField()  # Tracks performance for a specific month
    courses_created = models.PositiveIntegerField(default=0)
    students_engaged = models.PositiveIntegerField(default=0)
    webinars_conducted = models.PositiveIntegerField(default=0)
    assignments_graded = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Performance of {self.teacher} for {self.month}"
    

class TeacherStudentData(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='students_data')
    student = models.ForeignKey('Students.Student', on_delete=models.CASCADE, related_name='enrolled_courses')
    course = models.ForeignKey('Course_Module.Course', on_delete=models.CASCADE, related_name='student_enrollments')
    enrollment_date = models.DateTimeField(auto_now_add=True)
    progress = models.FloatField(default=0.0)  # Percentage of course completed
    grade = models.CharField(max_length=10, null=True, blank=True)  # Optional grade field

    def __str__(self):
        return f"{self.student} enrolled in {self.course} under {self.teacher}"
