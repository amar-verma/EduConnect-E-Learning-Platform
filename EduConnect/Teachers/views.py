import json
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render,redirect
from .models import Teacher,ReceivedPayment,PaidPayment,StudentQuery,Post,Comment,TeacherAward, TeacherFeedback, TeacherNotificationSettings, TeacherPayment,TeacherProfile
from django.contrib import messages
from Course_Module.models import Course,Content,Assignment,CourseComment,Certificate, EduOTP,StudentProgress,CourseFeatures,CourseSkills,CourseLearning,AssignmentSubmission
from Students.models import Student,TeacherNotificationDashBoard,StudentNotificationDashboard
from Edu_Main.models import User
from .forms import TeacherForm
from EduAssessment.models import Enrollment,Message,Form
from videoconference_app.models import Webinar
from datetime import datetime
from django.utils.timezone import localtime, now
from django.db.models import Count, Q , Sum, F
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.utils import simpleSplit
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import timedelta
from django.core.serializers.json import DjangoJSONEncoder
import random
import string
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError, OperationalError, transaction
from django.core.mail import send_mail


# Create your views here.

def tech_home(request):
    return render(request,'tech_index.html')

def send_otp_teacher(email,otp_type="verification"):
    """Generate and store OTP"""
    otp = random.randint(100000, 999999)  # 6-digit OTP
    otp_entry, created = EduOTP.objects.update_or_create(
        email=email, defaults={"otp": otp, "timestamp": now(), "is_verified": False}
    )
    # Send the OTP through email
    title = 'Your OTP Code'
    description = f'Your verification OTP code is {otp}. It will expire in 5 minutes.'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = email  

    
    
    if otp_type == "reset_password":
        description = f"Your OTP for resetting your password is {otp}. It will expire in 5 minutes."

    if otp_type == "resend_otp":
        description = f"Your new OTP is {otp}. It will expire in 5 minutes."

    if otp_type == "register":
        description = f"Your EduConnect Registration OTP is {otp}. It will expire in 5 minutes."
    
    # send_mail(title,description,from_email,[to_email], fail_silently=False,)
    print(f"OTP Sent to {email}: {otp} : {description}")  
    return otp 



def tech_login(request):
    context={}
    if request.user.is_authenticated:
        if request.user.user_type == 'teacher':
            return redirect('tech_overview')
        else:
            messages.error(request, 'You must be a teacher to access the teacher dashboard.')
            return redirect('std_login')
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if both username and password are provided
        if not username or not password:
            messages.error(request, 'Both username and password are required.')
            return redirect('tech_login')  

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.user_type == 'teacher':
                # Check if the teacher exists in the Teacher model
                try:
                    teacher = Teacher.objects.get(user=user)
                    
                    if not teacher.first_name or not teacher.last_name: 
                        messages.warning(request, 'Please complete your profile first.')
                        return redirect('tech_reprofile', username) 
                    try:
                        notification_settings, created = TeacherNotificationSettings.objects.get_or_create(teacher=teacher)
                        if notification_settings.auth_notifications:
                            otp = send_otp_teacher(user.email,otp_type="verification")
                            request.session["otp_email_teacher"] = user.email
                            return redirect("verify_otp_teacher")
                        else:
                            login(request, user)
                            return redirect('tech_overview')
                    except TeacherNotificationSettings.DoesNotExist:
                        messages.warning(request, 'Please configure your notification settings.')
                        return redirect('/')  
                except Teacher.DoesNotExist:
                    return redirect('tech_reprofile', username) 
                
            elif user.user_type == 'student':
                messages.error(request, 'Invalid user.')
                redirect('tech_login')
            else:
                messages.error(request, 'No data found')
                return redirect('/')

        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('tech_login')


    return render(request,'tech_login.html',context)



def verify_otp_teacher(request):
    """Verify the entered OTP"""
    email = request.session.get("otp_email_teacher")
    if not email:
        return redirect("tech_login")

    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        otp_entry = EduOTP.objects.filter(email=email, is_verified=False).first()

        if otp_entry and not otp_entry.is_expired():
            if otp_entry.otp == int(entered_otp):
                otp_entry.is_verified = True
                otp_entry.save()
                user = User.objects.filter(email=email).first()
                login(request, user)
                return redirect("tech_overview")
            else:
                messages.error(request, "Incorrect OTP.")
        else:
            messages.error(request, "OTP expired. Please request a new one.")

    return render(request, "verify_otp_teacher.html", {"email": email})



def resend_otp_teacher(request):
    """Resend OTP if expired"""
    email = request.session.get("otp_email_teacher")
    if not email:
        return redirect("tech_login")
    
    referer_url = request.META.get('HTTP_REFERER', 'tech_login')


    otp_entry = EduOTP.objects.filter(email=email, is_verified=False).first()
    if otp_entry and not otp_entry.is_expired():
        remaining_time = 300 - (now() - otp_entry.timestamp).total_seconds()
        remaining_minutes = int(remaining_time // 60)
        remaining_seconds = int(remaining_time % 60)
        if remaining_minutes > 0:
            time_message = f"Your OTP is still valid for {remaining_minutes} minute{'s' if remaining_minutes > 1 else ''} and {remaining_seconds} second{'s' if remaining_seconds != 1 else ''}."
        else:
            time_message = f"Your OTP is still valid for {remaining_seconds} second{'s' if remaining_seconds != 1 else ''}."

        messages.info(request,time_message)
    else:
        send_otp_teacher(email,otp_type="resend_otp")
        messages.success(request, "A new OTP has been sent to your email.")

    return redirect(referer_url)



def forget_password_teacher(request):
    email_session = request.session.get("otp_email")
    if email_session:
        del request.session["otp_email"]

    if request.method == "POST":
        email = request.POST.get("email")
        
        try:
            user = User.objects.get(email=email, user_type='teacher')
            otp = send_otp_teacher(email,otp_type="reset_password")
            request.session["otp_email_teacher"] = email
            messages.success(request, "OTP sent to your email.")
            return redirect("tech_reset_password")
        except User.DoesNotExist:
            messages.error(request, "No instructor account found with this email.")
    
    return render(request, "tech_forgot.html")



def tech_reset_password(request):
    email = request.session.get("otp_email_teacher")
    if not email:
        return redirect("forget_password_teacher")

    if request.method == "POST":
        otp = request.POST.get("otp")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        otp_entry = EduOTP.objects.filter(email=email, is_verified=False).first()

        if otp_entry and not otp_entry.is_expired():
            if otp_entry.otp == int(otp):
                if new_password == confirm_password:
                    user = User.objects.get(email=email)
                    user.set_password(new_password)
                    user.save()
                    otp_entry.is_verified = True
                    otp_entry.save()
                    messages.success(request, "Password reset successful. Please login.")
                    return redirect("tech_login")
                else:
                    messages.error(request, "Passwords do not match.")
            else:
                messages.error(request, "Incorrect OTP.")
        else:
            messages.error(request, "OTP expired. Please request a new one.")

    return render(request, "tech_reset.html", {"email": email})



def tech_reprofile(request, username):
    context = {}
    try:
        user = User.objects.get(username=username)
        context['user'] = user

        if Teacher.objects.filter(user=user).exists():
            messages.error(request, "You already have an updated profile.")
            return redirect('tech_login')
        
    except User.DoesNotExist:
        messages.error(request, "User does not exist.")
        return redirect('tech_login')

    if request.method == 'POST':
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('cpassword', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        profile_picture = request.FILES.get('profile_picture') 
        phone_number = request.POST.get('phone_number', '').strip()
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        country = request.POST.get('country', '').strip()
        bio = request.POST.get('bio', '').strip()
        social_links = request.POST.get('social_links', '').strip()


        if not password or not confirm_password:
            messages.error(request, "Password and confirm password cannot be empty.")
            return redirect('tech_reprofile', username=username)

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('tech_reprofile', username=username)


        if not profile_picture or not phone_number or not address or not city or not state or not country or not bio:
            messages.error(request, "All fields are required.")
            return redirect('tech_reprofile', username=username)


        if len(phone_number) != 10 or not phone_number.isdigit():
            messages.error(request, "Phone number must be exactly 10 digits and contain only numbers.")
            return redirect('tech_reprofile', username=username)

        try:

            teacher, created = Teacher.objects.get_or_create(user=user)

            teacher.first_name = user.first_name
            teacher.last_name = user.last_name
            teacher.profile_picture = profile_picture
            teacher.phone_number = phone_number
            teacher.address = address
            teacher.city = city
            teacher.state = state
            teacher.country = country
            teacher.bio = bio
            teacher.social_links = social_links


            if password:
                user.set_password(password) 
                user.save()


            teacher.save()
            messages.success(request, 'Your profile is created or updated successfully!')
            return redirect('tech_login')

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('tech_reprofile', username=username)

    return render(request, 'tech_reprofile.html', context)


@login_required
def tech_overview(request):
    # Get current teacher
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')

    try:
        teacher = Teacher.objects.get(user=request.user)
        teacher_notifications = TeacherNotificationDashBoard.objects.filter(teacher=teacher).order_by('-created_at')[:25]

        
        # Get current date and last month date
        current_date = timezone.now()
        last_month = current_date - timedelta(days=30)
        
        # Basic Course Statistics
        courses = Course.objects.filter(teacher=teacher)
        total_courses = courses.count()
        total_enrollments = courses.aggregate(Sum('enroll'))['enroll__sum'] or 0
        
        # Calculate average rating based on likes/dislikes
        course_ratings = []
        for course in courses:
            if course.like + course.dislike > 0:
                rating = (course.like * 5) / (course.like + course.dislike)
                course_ratings.append(rating)
        avg_rating = sum(course_ratings) / len(course_ratings) if course_ratings else 0
        
        # Webinar and Event Statistics
        total_webinars = Webinar.objects.filter(teacher=teacher).count()
        total_events = Form.objects.filter(course__teacher=teacher).count()
        
        # Monthly Comparisons
        current_month_courses = courses.filter(created_at__gte=last_month).count()
        current_month_enrollments = courses.filter(created_at__gte=last_month).aggregate(Sum('enroll'))['enroll__sum'] or 0
        current_month_webinars = Webinar.objects.filter(teacher=teacher, scheduled_date__gte=last_month).count()
        current_month_events = Form.objects.filter(course__teacher=teacher, created_at__gte=last_month).count()
        
        # Previous month statistics
        prev_month = last_month - timedelta(days=30)
        prev_month_courses = courses.filter(created_at__range=(prev_month, last_month)).count()
        prev_month_enrollments = courses.filter(created_at__range=(prev_month, last_month)).aggregate(Sum('enroll'))['enroll__sum'] or 0
        prev_month_webinars = Webinar.objects.filter(teacher=teacher, scheduled_date__range=(prev_month, last_month)).count()
        prev_month_events = Form.objects.filter(course__teacher=teacher, created_at__range=(prev_month, last_month)).count()
        
        # Course completion data
        total_enrollment = Certificate.objects.filter(course__in=courses)
        completed_students = total_enrollment.values('student').distinct().count()  # Assuming all enrolled students complete the course
        
        # Course engagement data per course
        course_engagement = []
        for course in courses:
            engagement = {
                'title': course.title,
                'enrollments': course.enroll or 0,
                'likes': course.like,
                'dislikes': course.dislike
            }
            course_engagement.append(engagement)

        context = {
            'total_courses': total_courses,
            'total_enrollments': total_enrollments,
            'average_rating': round(avg_rating, 1),
            'total_webinars': total_webinars,
            'total_events': total_events,
            'completed_students': completed_students,
            'course_engagement': course_engagement,
            'teacher':teacher,
            'teacher_notifications':teacher_notifications,
            
            # Monthly comparisons
            'current_month': {
                'courses': current_month_courses,
                'enrollments': current_month_enrollments,
                'webinars': current_month_webinars,
                'events': current_month_events
            },
            'prev_month': {
                'courses': prev_month_courses,
                'enrollments': prev_month_enrollments,
                'webinars': prev_month_webinars,
                'events': prev_month_events
            }
        }
        
        context.update({
            'enrollment_data': json.dumps([{
                'month': course.created_at.strftime('%B'),
                'enrollments': course.enroll or 0,
                'title': course.title,
                'id':course.id
            } for course in courses]),
            
            'engagement_data': json.dumps([{
                'title': course.title,
                'likes': course.like,
                'dislikes': course.dislike
            } for course in courses])
        })
            
        return render(request, 'tech_overview.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('home')


#details related to course
@login_required
def tech_earning(request):
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')
    
    context= {}
    try:
        teacher = Teacher.objects.get(user=request.user)
        courses = Course.objects.filter(teacher_id=teacher.teacher_id)
        teacher_notifications = TeacherNotificationDashBoard.objects.filter(teacher=teacher).order_by('-created_at')[:25]
        
        course_data = []
        for course in courses:
            course_info = {
                "title": course.title,
                "course_id" : course.id,
                "total_content": course.content_items.count(),
                "total_forms": course.forms_course.count(),
                "total_assignments": Assignment.objects.filter(question__course=course).count(),
                "total_enrollments": course.enroll if course.enroll else 0,
                "course_status": "Active" if course.is_display else "Inactive",
                "total_webinars": course.webinars.count(),
                "total_likes": course.like,
                "total_dislikes": course.dislike,
            }
            course_data.append(course_info)
        context = {
            "course_data": course_data,
            "teacher":teacher,
            "teacher_notifications": teacher_notifications
        }

        return render(request, 'teac_course_status.html',context)
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')


@login_required
def update_course_status(request):
    if request.user.user_type != 'teacher':
        return JsonResponse({"error": "You must be an instructor to perform this action."}, status=403)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            course_id = data.get('course_id')
            teacher = Teacher.objects.get(user=request.user)
            course = Course.objects.get(id=course_id, teacher=teacher)
            course.is_display = not course.is_display
            course.save()

            new_status = "Active" if course.is_display else "Inactive"
            if not course.is_display:
                enrollments = Enrollment.objects.filter(course=course, status="Active")
                for enrollment in enrollments:
                    student = enrollment.student
                    notification_message = f"Course '{course.title}' has been set to inactive by the instructor."
                    
                    StudentNotificationDashboard.objects.create(
                        student=student,
                        message=notification_message,
                        is_read=False
                    )
            
            return JsonResponse({
                "success": True,
                "new_status": new_status
            })
            
        except Course.DoesNotExist:
            return JsonResponse({"error": "Course not found or you don't have permission to modify it."}, status=404)
        except Teacher.DoesNotExist:
            return JsonResponse({"error": "Teacher profile not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Invalid request method."}, status=400)


#used to diplay all the courses created by that teacher
@login_required
def tech_mycourse(request):
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')
    
    try:
        context = {}
        teacher = Teacher.objects.get(user=request.user)
        courses = Course.objects.filter(teacher=teacher)
        comment_counts = {course.id: CourseComment.objects.filter(course=course).count() for course in courses}
        teacher_notifications = TeacherNotificationDashBoard.objects.filter(teacher=teacher).order_by('-created_at')[:25]

        context['courses'] = courses
        context['comment_counts'] = comment_counts
        context['teacher'] =teacher
        context['teacher_notifications'] = teacher_notifications

        return render(request,'tech_mycourse.html',context)
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')


#used to show all the details reated to course
@login_required
def tech_course_detail(request, course_id):
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')
    try:
        teacher = Teacher.objects.get(user=request.user)
        teacher_notifications = TeacherNotificationDashBoard.objects.filter(teacher=teacher).order_by('-created_at')[:25]
        course = get_object_or_404(Course.objects.prefetch_related(
            'content_items', 'content_features', 'content_skills', 'content_learning', 'content_comment'
        ), id=course_id, teacher=teacher)

        context = {
            'course': course,
            'teacher':teacher,
            'teacher_notifications':teacher_notifications,
        }
        return render(request, 'tech_course_detail.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')
    


def generate_meeting_code():
    """Generate a unique meeting code"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if not Course.objects.filter(meeting_code=code).exists():
            return code








#===================================================================================
@login_required
def tech_create_course(request):
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')
    try:
        teacher = Teacher.objects.get(user=request.user)  # Replace with actual authentication
        courses = Course.objects.filter(teacher=teacher)
        categories = [
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
        ]
        return render(request, "tech_course.html", {"courses": courses,"categories": categories})
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('tech_overview')


@csrf_exempt
# def create_course(request):
#     teacher = Teacher.objects.get(user=request.user)
#     if request.method == 'POST':
#         try:
#             # Create course
#             course = Course.objects.create(
#                 title=request.POST['title'],
#                 description=request.POST['description'],
#                 description2=request.POST.get('description2'),
#                 duration=request.POST['duration'],
#                 price=request.POST['price'],
#                 old_price=request.POST.get('old_price'),
#                 max_enrollments=request.POST['max_enrollment'],
#                 is_display=request.POST.get('is_display') == 'on',
#                 teacher=teacher,
#                 category=request.POST['category'],
#                 meeting_code=generate_meeting_code()
#             )

#             tags_string = request.POST['tags']
#             tag_list = [tag.strip() for tag in tags_string.split(',')]
#             course.tags.add(*tag_list)

#             # Handle course image
#             if request.FILES.get('course_img'):
#                 course.course_img = request.FILES['course_img']
#                 course.save()

#             for field_name in ['features', 'skills', 'learning']:
#                 if field_name in request.POST:
#                     try:
#                         items = json.loads(request.POST[field_name])
#                         model = globals()[f'Course{field_name.capitalize()}']
#                         for item in items:
#                             if item.strip():  # Only create if not empty
#                                 model.objects.create(course=course, **{field_name: item})
#                     except json.JSONDecodeError:
#                         return JsonResponse({"success": False, "error": f"Invalid {field_name} data format"})

#             return JsonResponse({"success": True, "course_id": course.id})
#         except Exception as e:
#             return JsonResponse({"success": False, "error": str(e)})

#     return JsonResponse({"success": False, "error": "Invalid request method"})


@csrf_exempt
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == 'POST':
        try:
            # Update basic fields
            for field in ['title', 'description', 'description2', 'duration', 'category']:
                if field in request.POST:
                    setattr(course, field, request.POST[field])
            
            # Update numeric fields
            for field in ['price', 'old_price', 'max_enrollments']:
                if field in request.POST:
                    setattr(course, field, int(request.POST[field] or 0))
            
            # Update boolean fields
            course.is_display = request.POST.get('is_display') == 'on'
            
            # Handle image update
            if 'course_img' in request.FILES:
                if course.course_img:
                    course.course_img.delete()
                course.course_img = request.FILES['course_img']
            
            course.save()
            
            # Update tags
            if 'tags' in request.POST:
                course.tags.clear()
                tags = [tag.strip() for tag in request.POST['tags'].split(',')]
                course.tags.add(*tags)
            
            # Update dynamic fields
            for model, field in [
                (CourseFeatures, 'features'),
                (CourseSkills, 'skills'),
                (CourseLearning, 'learning')
            ]:
                if field in request.POST:
                    items = json.loads(request.POST[field])
                    model.objects.filter(course=course).delete()
                    for item in items:
                        model.objects.create(course=course, **{field: item})
            
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    
    # Handle GET request by returning course data
    course_data = {
        'id': course.id,
        'title': course.title,
        'description': course.description,
        'description2': course.description2,
        'duration': course.duration,
        'price': course.price,
        'old_price': course.old_price,
        'max_enrollment': course.max_enrollments,
        'is_display': course.is_display,
        'tags': ', '.join([tag.name for tag in course.tags.all()]),
        'category': course.category,
        'course_img': course.course_img.url if course.course_img else '',
        # 'features': list(course.content_features.values_list('features', flat=True)),
        # 'skills': list(course.content_skills.values_list('skills', flat=True)),
        # 'learning': list(course.content_learning.values_list('learn', flat=True)),
        'features': [feature.features for feature in course.content_features.all()],
        'skills': [skill.skills for skill in course.content_skills.all()],
        'learning': [learn.learn for learn in course.content_learning.all()],
    }
    return JsonResponse(course_data)



def get_course_content(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    contents = Content.objects.filter(course=course).order_by('order')
    
    content_data = [{
        "id": content.id,
        "title": content.title,
        "description": content.desc,
        "order": content.order,
        "assignments": list(content.content_assignment.values('id', 'title'))
    } for content in contents]
    
    return JsonResponse(content_data, safe=False)

@csrf_exempt
def update_content(request, content_id=None):
    if request.method == 'POST':
        try:
            if content_id:
                content = get_object_or_404(Content, id=content_id)
            else:
                print(request.POST['order'])
                print(request.POST['title'],)
                content = Content.objects.create(
                    course_id=request.POST['course_id'],
                    title=request.POST['title'],
                    order=request.POST['order']
                )
            
            content.title = request.POST['title']
            content.desc = request.POST['content']
            content.order = request.POST.get('order', 0)
            content.save()

            # Handle assignments
            Assignment.objects.filter(question=content).delete()
            for assignment_text in request.POST.getlist('assignments[]'):
                Assignment.objects.create(
                    question=content,
                    title=assignment_text
                )

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

@csrf_exempt
def delete_content(request, content_id):
    if request.method == 'DELETE':
        content = get_object_or_404(Content, id=content_id)
        content.delete()
        return JsonResponse({"success": True})

@csrf_exempt
def create_content(request):
    if request.method == 'POST':
        try:
            content = Content.objects.create(
                course_id=request.POST['course_id'],
                title=request.POST['title'],
                order=request.POST['order'],
                desc=request.POST['content']
            )

            # Create assignments for this content
            assignments = request.POST.getlist('assignments[]')
            for assignment_text in assignments:
                Assignment.objects.create(
                    question=content,
                    title=assignment_text
                )

            return JsonResponse({
                'success': True,
                'content_id': content.id
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })



def create_course(request):
    if request.method == 'POST':
        try:
            # Create Course
            course = Course.objects.create(
                title=request.POST['title'],
                description=request.POST['description'],
                description2=request.POST['description2'],
                category=request.POST['category'],
                duration=request.POST['duration'],
                price=request.POST['price'],
                old_price=request.POST['old_price'],
                teacher=request.user.teacher  # Assuming logged in user is a teacher
            )
            
            if 'course_img' in request.FILES:
                course.course_img = request.FILES['course_img']
                course.save()

            # Create Features
            features = request.POST.getlist('features[]')
            for feature in features:
                if feature:
                    CourseFeatures.objects.create(
                        course=course,
                        features=feature
                    )

            # Create Skills
            skills = request.POST.getlist('skills[]')
            for skill in skills:
                if skill:
                    CourseSkills.objects.create(
                        course=course,
                        skills=skill
                    )

            # Create Learning Outcomes
            learning_outcomes = request.POST.getlist('learning[]')
            for outcome in learning_outcomes:
                if outcome:
                    CourseLearning.objects.create(
                        course=course,
                        learn=outcome
                    )

            # Create Content and Assignments
            content_titles = request.POST.getlist('content_title[]')
            content_descriptions = request.POST.getlist('content_description[]')
            content_orders = request.POST.getlist('content_order[]')
            assignment_titles = request.POST.getlist('assignment_title[]')

            for i in range(len(content_titles)):
                content = Content.objects.create(
                    course=course,
                    title=content_titles[i],
                    description=content_descriptions[i],
                    order=content_orders[i]
                )

                # Create assignments for this content
                if i < len(assignment_titles) and assignment_titles[i]:
                    Assignment.objects.create(
                        question=content,
                        title=assignment_titles[i]
                    )

            messages.success(request, 'Course created successfully!')
            return redirect('course_list')  # Replace with your course list URL name

        except Exception as e:
            messages.error(request, f'Error creating course: {str(e)}')
            return redirect('create_course')

    return render(request, 'courses/course_form.html')

def update_course(request, course_id):
    course = Course.objects.get(id=course_id)
    
    if request.method == 'POST':
        try:
            # Update Course
            course.title = request.POST['title']
            course.description = request.POST['description']
            course.description2 = request.POST['description2']
            course.category = request.POST['category']
            course.duration = request.POST['duration']
            course.price = request.POST['price']
            course.old_price = request.POST['old_price']

            if 'course_img' in request.FILES:
                course.course_img = request.FILES['course_img']
            course.save()

            # Update Features
            CourseFeatures.objects.filter(course=course).delete()
            features = request.POST.getlist('features[]')
            for feature in features:
                if feature:
                    CourseFeatures.objects.create(course=course, features=feature)

            # Update Skills
            CourseSkills.objects.filter(course=course).delete()
            skills = request.POST.getlist('skills[]')
            for skill in skills:
                if skill:
                    CourseSkills.objects.create(course=course, skills=skill)

            # Update Learning Outcomes
            CourseLearning.objects.filter(course=course).delete()
            learning_outcomes = request.POST.getlist('learning[]')
            for outcome in learning_outcomes:
                if outcome:
                    CourseLearning.objects.create(course=course, learn=outcome)

            # Update Content and Assignments
            Content.objects.filter(course=course).delete()
            content_titles = request.POST.getlist('content_title[]')
            content_descriptions = request.POST.getlist('content_description[]')
            content_orders = request.POST.getlist('content_order[]')
            assignment_titles = request.POST.getlist('assignment_title[]')

            for i in range(len(content_titles)):
                content = Content.objects.create(
                    course=course,
                    title=content_titles[i],
                    description=content_descriptions[i],
                    order=content_orders[i]
                )

                if i < len(assignment_titles) and assignment_titles[i]:
                    Assignment.objects.create(
                        question=content,
                        title=assignment_titles[i]
                    )

            messages.success(request, 'Course updated successfully!')
            return redirect('course_list')

        except Exception as e:
            messages.error(request, f'Error updating course: {str(e)}')
            return redirect('update_course', course_id=course_id)

    context = {
        'course': course,
        'features': course.content_features.all(),
        'skills': course.content_skills.all(),
        'learning': course.content_learning.all(),
        'contents': course.content_items.all()
    }
    return render(request, 'courses/course_form.html', context)


#===================================================================================





#is to create course with content
@login_required
def create_course_z(request):
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')
    context={}
    try:
        teacher = Teacher.objects.get(user=request.user)
        context['teacher'] = teacher
        teacher_notifications = TeacherNotificationDashBoard.objects.filter(teacher=teacher).order_by('-created_at')[:25]
        context['teacher_notifications'] = teacher_notifications

        if request.method == 'POST':
            try:
                # Check for required fields
                required_fields = ['title', 'description', 'description2', 'duration', 'category', 'old_price', 'price', 'max_enroll']
                for field in required_fields:
                    if not request.POST.get(field):
                        messages.error(request, f'{field} is required.')  
                        return redirect('create_course_z')

                # Create Course
                course = Course.objects.create(
                    title=request.POST['title'],
                    description=request.POST['description'],
                    description2=request.POST['description2'],
                    teacher=request.user.teacher,
                    duration=request.POST['duration'],
                    category=request.POST['category'],
                    old_price=request.POST['old_price'],
                    price=request.POST['price'],
                    enroll=0,
                    max_enrollments=request.POST['max_enroll'],
                    meeting_code=generate_meeting_code()
                )

                if 'course_img' in request.FILES:
                    course.course_img = request.FILES['course_img']
                    course.save()

                # Create Learning Objectives
                learning_items = request.POST.getlist('learning[]')
                for item in learning_items:
                    if item:
                        CourseLearning.objects.create(course=course, learn=item)

                # Create Skills
                skills_items = request.POST.getlist('skills[]')
                for item in skills_items:
                    if item:
                        CourseSkills.objects.create(course=course, skills=item)

                # Create Features
                features_items = request.POST.getlist('features[]')
                for item in features_items:
                    if item:
                        CourseFeatures.objects.create(course=course, features=item)

                # Create Content and Assignments
                content_titles = request.POST.getlist('content_title[]')
                content_descs = request.POST.getlist('content_desc[]')
                content_orders = request.POST.getlist('content_order[]')
                assignment_titles = request.POST.getlist('assignment_title[]')

                for i in range(len(content_titles)):
                    content = Content.objects.create(
                        course=course,
                        title=content_titles[i],
                        desc=content_descs[i],
                        order=content_orders[i]
                    )

                    # Create assignments for this content
                    if i < len(assignment_titles):
                        Assignment.objects.create(
                            question=content,
                            title=assignment_titles[i]
                        )

                messages.success(request, 'Course Created Successfully...')
                return redirect('create_course_z')

            except IntegrityError as e:
                messages.error(request, f'Error creating course: {str(e)}')
            except OperationalError as e:
                messages.error(request, f'Error connecting to the database: {str(e)}')
            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {str(e)}")

            
            return redirect('create_course_z')

        return render(request, 'z_create.html',context)
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')


#is to update course info and content
@login_required
def update_course_z(request, course_id):
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')
    try:
        teacher = Teacher.objects.get(user=request.user)
        course = get_object_or_404(Course, id=course_id, teacher=teacher)
        teacher_notifications = TeacherNotificationDashBoard.objects.filter(teacher=teacher).order_by('-created_at')[:25]
        if request.method == 'POST':
            try:
                with transaction.atomic():  # ✅ Ensures rollback if any error occurs
                    changed_fields = {}
                    for field in ['title', 'description', 'description2', 'duration', 'category', 'old_price', 'price', 'max_enrollments']:
                        new_value = request.POST.get(field)
                        if str(getattr(course, field)) != new_value:
                            changed_fields[field] = new_value
                    
                    if changed_fields:
                        for field, value in changed_fields.items():
                            setattr(course, field, value)

                    if 'course_img' in request.FILES:
                        course.course_img = request.FILES['course_img']
                    
                    course.save()

                    # ✅ Handle learning objectives updates
                    current_learning = set(course.content_learning.values_list('learn', flat=True))
                    new_learning = set(filter(None, request.POST.getlist('learning[]')))
                    course.content_learning.filter(learn__in=current_learning - new_learning).delete()
                    for item in new_learning - current_learning:
                        CourseLearning.objects.create(course=course, learn=item)

                    # ✅ Handle skills updates
                    current_skills = set(course.content_skills.values_list('skills', flat=True))
                    new_skills = set(filter(None, request.POST.getlist('skills[]')))
                    course.content_skills.filter(skills__in=current_skills - new_skills).delete()
                    for item in new_skills - current_skills:
                        CourseSkills.objects.create(course=course, skills=item)

                    # ✅ Handle features updates
                    current_features = set(course.content_features.values_list('features', flat=True))
                    new_features = set(filter(None, request.POST.getlist('features[]')))
                    course.content_features.filter(features__in=current_features - new_features).delete()
                    for item in new_features - current_features:
                        CourseFeatures.objects.create(course=course, features=item)

                    # ✅ Handle content updates and creation
                    content_titles = request.POST.getlist('content_title[]')
                    content_descs = request.POST.getlist('content_desc[]')
                    content_orders = request.POST.getlist('content_order[]')
                    content_ids = request.POST.getlist('content_id[]')

                    valid_content_ids = []  # Track valid content IDs to prevent deletion

                    # 🟢 Step 1: Update existing content
                    for i in range(len(content_titles)):
                        content_id = content_ids[i].strip() if i < len(content_ids) and content_ids[i] else None
                        if content_id and content_id.isdigit():
                            content = Content.objects.get(id=int(content_id))
                            content.title = content_titles[i]
                            content.desc = content_descs[i]
                            content.order = int(content_orders[i]) if content_orders[i].strip().isdigit() else 0
                            content.save()

                            # ✅ Track valid content IDs
                            valid_content_ids.append(content.id)

                            # ✅ Handle assignment updates for existing content
                            existing_assignments = set(Assignment.objects.filter(question=content).values_list('title', flat=True))
                            new_assignments = set(filter(None, request.POST.getlist(f'assignment_title_{i}[]')))

                            # ✅ Remove deleted assignments
                            Assignment.objects.filter(question=content, title__in=(existing_assignments - new_assignments)).delete()

                            # ✅ Add new assignments
                            for item in new_assignments - existing_assignments:
                                Assignment.objects.create(question=content, title=item)

                    # 🟢 Step 2: Create new content
                    for i in range(len(content_titles)):
                        content_id = content_ids[i].strip() if i < len(content_ids) and content_ids[i] else None
                        if not content_id or not content_id.isdigit():
                            new_content = Content.objects.create(
                                course=course,
                                title=content_titles[i],
                                desc=content_descs[i],
                                order=int(content_orders[i]) if content_orders[i].strip().isdigit() else 0
                            )
                            valid_content_ids.append(new_content.id)

                            # ✅ Handle assignment creation for new content
                            new_assignments = set(filter(None, request.POST.getlist(f'assignment_title_{i}[]')))
                            for item in new_assignments:
                                Assignment.objects.create(question=new_content, title=item)

                    # ✅ Step 3: Handle deleted content properly
                    if valid_content_ids:
                        course.content_items.exclude(id__in=valid_content_ids).delete()

                    messages.success(request, 'Course updated successfully!')
                    return redirect('tech_course_detail', course_id=course.id)

            except IntegrityError as e:
                messages.error(request, f"Database integrity error: {e}")
                return redirect('update_course_z', course_id=course.id)

            except OperationalError as e:
                messages.error(request, f"Database connection error: {e}")
                return redirect('update_course_z', course_id=course.id)

            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {e}")
                return redirect('tech_overview')

        # ✅ Pass data to the template
        context = {
            'course': course,
            'learning_objectives': course.content_learning.all(),
            'skills': course.content_skills.all(),
            'features': course.content_features.all(),
            'contents': course.content_items.all().prefetch_related('content_assignment'),
            'teacher': teacher,
            'teacher_notifications': teacher_notifications
        }
        return render(request, 'z_update_course.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')



#to check student submitted assignment..
@login_required
def tech_assignments(request):
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')
    
    try:
        teacher = Teacher.objects.get(user=request.user)
        teacher_notifications = TeacherNotificationDashBoard.objects.filter(teacher=teacher).order_by('-created_at')[:25]
        
        # Get courses taught by this teacher
        teacher_courses = Course.objects.filter(teacher=teacher)
        
        # Get all assignments from teacher's courses
        course_contents = Content.objects.filter(course__in=teacher_courses)
        assignments = Assignment.objects.filter(question__in=course_contents)
        
        # Get all submissions for these assignments
        submissions = AssignmentSubmission.objects.filter(
            assignment__in=assignments
        ).select_related('student', 'assignment', 'assignment__question__course')
        
        # Handle submission status update
        if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = json.loads(request.body)
            submission_id = data.get('submission_id')
            new_status = data.get('status')
            message = data.get('message', '')
            
            try:
                submission = AssignmentSubmission.objects.get(id=submission_id)
                old_status = submission.status
                submission.status = new_status
                submission.message = message
                submission.save()
                
                # Create notification for student
                status_text = "marked as complete" if new_status == "completed" else "needs rework"
                notification_message = f"Your assignment '{submission.assignment.title}' has been {status_text}."
                if message:
                    notification_message += f" Message: {message}"
                
                StudentNotificationDashboard.objects.create(
                    student=submission.student,
                    message=notification_message,
                    is_read=False
                )
                
                return JsonResponse({
                    'success': True, 
                    'message': f'Submission updated from {old_status} to {new_status}'
                })
            except AssignmentSubmission.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Submission not found'}, status=404)
            except Exception as e:
                return JsonResponse({'success': False, 'message': str(e)}, status=500)
        
        # Get filter parameters
        student_name = request.GET.get('student_name', '')
        course_id = request.GET.get('course_id', '')
        status = request.GET.get('status', '')
        
        # Apply filters
        if student_name:
            submissions = submissions.filter(
                Q(student__first_name__icontains=student_name) | 
                Q(student__last_name__icontains=student_name)
            )
        
        if course_id:
            submissions = submissions.filter(assignment__question__course_id=course_id)
        
        if status:
            submissions = submissions.filter(status=status)
        
        context = {
            'teacher': teacher,
            'teacher_notifications': teacher_notifications,
            'submissions': submissions,
            'teacher_courses': teacher_courses,
            'filters': {
                'student_name': student_name,
                'course_id': course_id,
                'status': status
            }
        }
        
        return render(request, 'tech_assignment.html', context)
    
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')




#its to render all the student data for certificate
@login_required
def tech_certificate(request):
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')
    try:
        teacher = Teacher.objects.get(user = request.user)  
        courses = Course.objects.filter(teacher=teacher)  
        enrollments = Enrollment.objects.filter(course__in=courses).select_related('student', 'course')
        teacher_notifications = TeacherNotificationDashBoard.objects.filter(teacher=teacher).order_by('-created_at')[:25]

        student_data = []
        issued_students = 0  # Counter for issued certificates

        for enrollment in enrollments:
            progress = StudentProgress.objects.filter(student=enrollment.student, content__course=enrollment.course)
            completed = all(p.is_completed for p in progress) if progress.exists() else False

            # Check if a certificate exists for this student and course
            certificate = Certificate.objects.filter(student=enrollment.student, course=enrollment.course).first()
            certificate_issued = certificate is not None  

            if certificate_issued:
                issued_students += 1  # Count issued certificates

            student_data.append({
                'student_id': enrollment.student.student_id,
                'name': f"{enrollment.student.first_name} {enrollment.student.last_name}",
                'course': enrollment.course.title,
                'enrolled_date': enrollment.enrollment_date,
                'months': enrollment.course.months,
                'course_id': enrollment.course.id,
                'status': "Completed" if completed else "Active",
                'certificate_issued': certificate_issued,
                'certificate_date': certificate.created_at if certificate else None
            })

        total_students = len(student_data)  # Count total students
        pending_students = total_students - issued_students  # Calculate pending certificates

        return render(request, "tech_certificate.html", {"students": student_data,"total_students": total_students,"issued_students": issued_students,"pending_students": pending_students,'teacher':teacher,'teacher_notifications':teacher_notifications})
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')
    


#its to convert true(entering data)
@csrf_exempt
def issue_certificate(request):
    if request.method == "POST":
        data = json.loads(request.body)
        student_id = data.get("student_id")
        course_id = data.get("course_id")
        
        # Get student and course objects
        try:
            student = Student.objects.get(student_id=student_id)
            course = Course.objects.get(id=course_id)
        except (Student.DoesNotExist, Course.DoesNotExist):
            return JsonResponse({"error": "Student or course not found"}, status=404)
        
        # Check if certificate already exists
        if Certificate.objects.filter(student_id=student_id, course_id=course_id).exists():
            return JsonResponse({"error": "Certificate already issued"}, status=400)
        
        # Calculate progress percentage (similar to enroll_course view)
        content_list = Content.objects.filter(course=course).order_by('id')
        
        # Calculate total points for course
        total_contents = content_list.count()  # Each content = 1 point
        total_assignments = Assignment.objects.filter(question__in=content_list).count()  # Each assignment = 2 points
        total_possible_points = (total_contents * 1) + (total_assignments * 2)
        
        # Calculate earned points by student
        completed_contents = StudentProgress.objects.filter(student=student, content__in=content_list, is_completed=True).count()
        submitted_assignments = AssignmentSubmission.objects.filter(student=student, assignment__question__in=content_list).count()
        earned_points = (completed_contents * 1) + (submitted_assignments * 2)
        
        # Compute progress percentage
        progress_percentage = (earned_points / total_possible_points) * 100 if total_possible_points > 0 else 0
        progress_percentage = round(progress_percentage, 2)  # Round to 2 decimal places
        
        # Check if progress is 100%
        if progress_percentage < 100:
            return JsonResponse({"error": "Cannot issue certificate. Course progress is not 100% complete."}, status=400)
        
        # Create certificate
        certificate = Certificate.objects.create(
            student_id=student_id, 
            course_id=course_id
        )
        
        # Send email to student
        try:
            title = f'Certificate for {course.title}'
            description = f'''
            Congratulations {student.user.first_name}!
            
            You have successfully completed the course "{course.title}" and your certificate has been issued.
            
            You can view and download your certificate from your dashboard.
            
            Thank you for learning with us!
            
            Best regards,
            EduConnect Team
            '''
            
            from_email = settings.DEFAULT_FROM_EMAIL  # Use your configured email in settings
            to_email = student.user.email
            
            #send_mail(title,description,from_email,[to_email],fail_silently=False,)
            
            # Create notification for the student
            StudentNotificationDashboard.objects.create(
                student=student,
                message=f"Congratulations! Your certificate for '{course.title}' has been issued.",
                is_read=False
            )
            
            return JsonResponse({
                "success": True, 
                "issued_on": certificate.created_at.strftime("%Y-%m-%d"),
                "email_sent": True
            })
            
        except Exception as e:
            # If email fails, still return success but note email failure
            return JsonResponse({
                "success": True, 
                "issued_on": certificate.created_at.strftime("%Y-%m-%d"),
                "email_sent": False,
                "email_error": str(e)
            })

    return JsonResponse({"error": "Invalid request"}, status=400)


#its used to fetch all the form details created by that teacher
@login_required
def tech_grade(request):
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')
    context = {}
    try:
        teacher = Teacher.objects.get(user=request.user)
        teacher_notifications = TeacherNotificationDashBoard.objects.filter(teacher=teacher).order_by('-created_at')[:25]
        forms = Form.objects.filter(course__teacher=teacher)
        context['forms'] = forms
        context['teacher'] = teacher
        context['teacher_notifications'] = teacher_notifications
        return render(request,'tech_grade.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')


#this is for to render quries of student 
@login_required
def tech_quries(request):
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')
    try:
        teacher = Teacher.objects.get(user=request.user)
        teacher_courses = Course.objects.filter(teacher=teacher)  
        teacher_notifications = TeacherNotificationDashBoard.objects.filter(teacher=teacher).order_by('-created_at')[:25]
        student_queries = StudentQuery.objects.filter(course__in=teacher_courses).order_by('-created_at')

        return render(request, 'tech_queries.html', {'student_queries': student_queries,'teacher':teacher,'teacher_notifications':teacher_notifications})
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')
    


#this is for answer to student quries
@login_required
def answer_query(request, query_id):
    query = get_object_or_404(StudentQuery, id=query_id)

    if request.method == "POST":
        response_text = request.POST.get('response_text')
        if response_text:
            query.response_text = response_text
            query.status = 'resolved'
            query.save()
    
    return redirect('tech_quries')


#this is to render the post 
@login_required
def tech_forums(request):
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')
    try:
        teacher = Teacher.objects.get(user=request.user)  
        teacher_notifications = TeacherNotificationDashBoard.objects.filter(teacher=teacher).order_by('-created_at')[:25]
        courses = Course.objects.filter(teacher=teacher) 
        posts = Post.objects.filter(course__in=courses).order_by('-created_at')  

        return render(request, 'tech_forums.html', {'posts': posts, 'courses': courses,'teacher':teacher,'teacher_notifications':teacher_notifications})
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')


#is to create a post by teacher
@login_required
def create_post(request):
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')
    try:
        if request.method == "POST":
            teacher = Teacher.objects.get(user=request.user)
            course_id = request.POST.get('course_id')
            content = request.POST.get('content')

            course = get_object_or_404(Course, id=course_id, teacher=teacher)  
            post = Post.objects.create(teacher=teacher, course=course, content=content)

            enrollments = Enrollment.objects.filter(course=course, status="Active")
            for enrollment in enrollments:
                student = enrollment.student
                notification_message = f"New post from {teacher.first_name} {teacher.last_name} in course '{course.title}'"

                StudentNotificationDashboard.objects.create(
                    student=student,
                    message=notification_message,
                    is_read=False
                )

            return JsonResponse({"message": "Post created successfully!"})
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')


#to add comment by student and teacher
@login_required
def add_comment(request, post_id):
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')
    try:    
        if request.method == "POST":
            try:
                data = json.loads(request.body)
                content = data.get("content")
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON data."}, status=400)

            post = get_object_or_404(Post, id=post_id)
            if not content:
                return JsonResponse({"error": "Comment content cannot be empty."}, status=400)

            # Fetch the teacher (Replace with actual authentication logic)
            teacher = Teacher.objects.get(user=request.user)
            if teacher:
                Comment.objects.create(post=post, content=content, teacher=teacher)
                return JsonResponse({"message": "Comment added successfully!"})

            return JsonResponse({"error": "Teacher not found."}, status=404)

        return JsonResponse({"error": "Invalid request method."}, status=405)
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')


#to delete the post created by that teacher
@login_required
def delete_post(request, post_id):
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')
    try:
        teacher = Teacher.objects.get(user=request.user)
        if request.method == "DELETE":
            post = get_object_or_404(Post, id=post_id)
            
            # Ensure only the teacher who created the post can delete it
            if teacher.user.email == post.teacher.user.email:
                post.delete()
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"error": "You do not have permission to delete this post."}, status=403)

        return JsonResponse({"error": "Invalid request method."}, status=400)
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')
    


#used to render all the courses comment with its like & dislike
@login_required
def tech_review(request):
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')
    try:
        teacher = Teacher.objects.get(user=request.user) 
        teacher_notifications = TeacherNotificationDashBoard.objects.filter(teacher=teacher).order_by('-created_at')[:25]
        courses = Course.objects.filter(teacher=teacher)  
        comments = CourseComment.objects.filter(course__in=courses)

        total_likes = comments.filter(value=True).count()
        total_dislikes = comments.filter(value=False).count()
        total_votes = total_likes + total_dislikes
        like_percentage = (total_likes / total_votes) * 100 if total_votes > 0 else 0
        dislike_percentage = (total_dislikes / total_votes) * 100 if total_votes > 0 else 0

        context = {
            'comments': comments,
            'total_likes': total_likes,
            'total_dislikes': total_dislikes,
            'like_percentage': round(like_percentage, 2),
            'dislike_percentage': round(dislike_percentage, 2),
            'total_votes': total_votes,
            'teacher':teacher,
            'teacher_notifications':teacher_notifications,
        }
        
        return render(request, 'tech_review.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')
    


#used to send a message to student
@login_required
def tech_message(request):
    if request.user.user_type != 'teacher': 
            messages.error(request, "You must be a instructor to access this page.")
            return redirect('tech_login')
    try:
        teacher = Teacher.objects.get(user=request.user)  
        teacher_notifications = TeacherNotificationDashBoard.objects.filter(teacher=teacher).order_by('-created_at')[:25]
        courses = Course.objects.filter(teacher=teacher).prefetch_related("enrolled_students__student")  
        messages_data = Message.objects.filter(teacher=teacher).order_by("-created_at")  

        success_message = None
        error_message = None

        if request.method == "POST":
            course_id = request.POST.get("course_id")
            student_id = request.POST.get("student_id")
            message_text = request.POST.get("message")

            if course_id and student_id and message_text:
                try:
                    course = Course.objects.get(id=course_id, teacher=teacher)
                    student = Student.objects.get(student_id=student_id, enrollments__course=course)

                    # Save message
                    Message.objects.create(
                        teacher=teacher,
                        student=student,
                        course=course,
                        message=message_text,
                    )
                    # Create notification for the student
                    notification_message = f"You have a new message from {teacher.first_name} {teacher.last_name} in course '{course.title}'"
                    StudentNotificationDashboard.objects.create(
                        student=student,
                        message=notification_message,
                        is_read=False
                    )
                    

                    success_message = "Message sent successfully!"
                except Exception as e:
                    error_message = f"Failed to send message: {str(e)}"

        return render(request, "tech_message.html", {"courses": courses,"messages": messages_data,"success_message": success_message,"error_message": error_message,'teacher':teacher,'teacher_notifications':teacher_notifications})
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')


def tech_emails(request):
    return render(request,'tech_course_status.html')


#used to schedule meeting
@login_required
def tech_meeting(request):
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')
    try:
        context={}
        teacher = Teacher.objects.get(user=request.user)
        teacher_notifications = TeacherNotificationDashBoard.objects.filter(teacher=teacher).order_by('-created_at')[:25]
        current_date = localtime(now()).date()  
        webinars = Webinar.objects.filter(course__teacher=teacher)
        
        for webinar in webinars:
            if webinar.scheduled_date.date() != current_date: 
                webinar.status = False
                webinar.meeting_link = None
                webinar.save()

        if request.method == "POST":
            title = request.POST.get("meetingTitle")
            course_id = request.POST.get("courseSelect")
            date = request.POST.get("meetingDate")
            desc = request.POST.get("desc") 

            if not desc:
                desc ="EduConnect Meeting For Students"

            if title and course_id and date:
                try:
                    course = Course.objects.get(id=course_id)
                    current_time = now().time()
                    scheduled_datetime = datetime.strptime(date, "%Y-%m-%d").replace(
                        hour=current_time.hour,
                        minute=current_time.minute,
                        second=current_time.second
                    )

                    Webinar.objects.create(
                        title=title,
                        course=course,
                        description=desc,
                        teacher=teacher,
                        scheduled_date=scheduled_datetime
                    )
                    enrollments = Enrollment.objects.filter(course=course, status="Active")
                    for enrollment in enrollments:
                        student = enrollment.student
                        message = f"A new webinar titled '{webinar.title}' has been scheduled for your course '{course.title}'."
                        
                        # Create a new notification for the student
                        StudentNotificationDashboard.objects.create(
                            student=student,
                            message=message,
                            is_read=False
                        )
                    messages.success(request, "Webinar successfully scheduled!")
                except Exception as e:
                    messages.error(request, f"Failed to schedule webinar: {str(e)}")
            else:
                messages.error(request, "All fields are required!")

            return redirect("tech_meeting") 

        courses = Course.objects.filter(teacher=teacher)
        webinars_by_course = {
            course: Webinar.objects.filter(course=course, teacher=teacher).order_by("-scheduled_date")
            for course in courses if Webinar.objects.filter(course=course, teacher=teacher).exists()
        }

        return render(request, "tech_meeting.html", {"courses": courses, "webinars_by_course": webinars_by_course,"current_date": current_date,"teacher":teacher,'teacher_notifications':teacher_notifications})
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')

#used to turn off and on meeting
@login_required
def toggle_webinar_status(request, webinar_id):
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')
    try:
        webinar = get_object_or_404(Webinar, id=webinar_id)
        
        # Only allow status change if today is the scheduled date
        if webinar.scheduled_date.date() == now().date():
            webinar.status = not webinar.status  # Toggle status
            if webinar.status:
                webinar.meeting_link = webinar.course.meeting_code
            else:
                webinar.meeting_link = None
            webinar.save()
            messages.success(request, "Webinar status updated successfully!")
        else:
            messages.error(request, "You can only update the status on the scheduled date.")

        return redirect("tech_meeting")  # Redirect back to the page
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')


#used to display all income & expenese
@login_required
def tech_rpay(request):
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')
    try:
        teacher = Teacher.objects.get(user=request.user)
        teacher_notifications = TeacherNotificationDashBoard.objects.filter(teacher=teacher).order_by('-created_at')[:25]
        received_payments = ReceivedPayment.objects.filter(course__teacher=teacher)
        paid_payments = PaidPayment.objects.filter(teacher=teacher)

        total_received = sum(payment.amount for payment in received_payments)
        total_paid = sum(payment.amount for payment in paid_payments)


        total_earnings = ReceivedPayment.objects.filter(course__teacher=teacher).aggregate(Sum('amount'))['amount__sum'] or 0

        # Monthly Earnings (Current Month)
        current_month = datetime.now().month
        monthly_earnings = ReceivedPayment.objects.filter(
            course__teacher=teacher, payment_date__month=current_month
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        # Last Month Earnings for Comparison
        last_month = (datetime.now() - timedelta(days=30)).month
        last_month_earnings = ReceivedPayment.objects.filter(
            course__teacher=teacher, payment_date__month=last_month
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        earnings_growth = ((monthly_earnings - last_month_earnings) / last_month_earnings * 100) if last_month_earnings else 0

        total_expenses = PaidPayment.objects.filter(teacher=teacher).aggregate(Sum('amount'))['amount__sum'] or 0

        # Course-wise Earnings Breakdown
        course_earnings = list(ReceivedPayment.objects.filter(course__teacher=teacher)
            .values('course__title')
            .annotate(total_earned=Sum('amount'))
            .order_by('-total_earned')
        )

        # Prepare JSON Data for Charts
        income_vs_expenses = {'labels': ['Income', 'Expenses'], 'data': [total_earnings, total_expenses]}


        context = {
            "received_payments": received_payments,
            "paid_payments": paid_payments,
            "total_received": total_received,
            "total_paid": total_paid,
            'total_earnings': total_earnings,
            'monthly_earnings': monthly_earnings,
            'earnings_growth': earnings_growth,
            'total_expenses': total_expenses,
            'course_earnings': course_earnings,
            'income_vs_expenses': income_vs_expenses,
            'teacher':teacher,
            'teacher_notifications':teacher_notifications
        }
        return render(request, "tech_paidpay.html", context)
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')





#used to update info of teacher
@login_required
def tech_setting(request):
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')
    try:
        teacher = get_object_or_404(Teacher, user=request.user)  
        teacher_notifications = TeacherNotificationDashBoard.objects.filter(teacher=teacher).order_by('-created_at')[:25]
        profile, created = TeacherProfile.objects.get_or_create(teacher=teacher)
        awards = TeacherAward.objects.filter(teacher=teacher)
        settings = TeacherNotificationSettings.objects.filter(teacher=teacher).first()
        payments = TeacherPayment.objects.filter(teacher=teacher)
        total_amount_due = sum(p.amount for p in payments if p.status == "pending")

        if request.method == "POST":
            # first_name = request.POST.get("first_name", "").strip()
            # last_name = request.POST.get("last_name", "").strip()
            
            phone_number = request.POST.get("phone_number", "").strip()
            bio = request.POST.get("bio", "").strip()
            qualifications = request.POST.get("qualifications", "").strip()
            experience = request.POST.get("experience", "").strip()
            specializations = request.POST.get("specializations", "").strip()
            interest = request.POST.get("interest", "").strip()
            languages_spoken = request.POST.get("languages_spoken", "").strip()
            linkedin = request.POST.get("linkedin", "").strip()
            github = request.POST.get("github", "").strip()
            philosophy = request.POST.get("philosophy", "").strip()
            availability = request.POST.getlist("availability")
            profile_picture = request.FILES.get("profile_picture")
            social_link = request.POST.get("social_link")

            if not all([phone_number, bio, qualifications, experience]):
                messages.error(request, "All fields are required. Please fill in all fields.")
                return redirect("tech_setting")
            if len(phone_number) == 10 and phone_number.isdigit():
                teacher.phone_number = phone_number
            else:
                messages.error(request, "phone number is not valid")
                return redirect("tech_setting")

            # teacher.phone_number = phone_number
            teacher.bio = bio
            if profile_picture:
                teacher.profile_picture = profile_picture
            if social_link:
                teacher.social_links = social_link
            teacher.save()

            
            profile.qualifications = qualifications
            profile.experience_years = experience
            profile.specializations = specializations
            profile.interest = interest
            profile.languages_spoken = languages_spoken
            profile.social_links_linkedin = linkedin
            profile.social_links_github = github
            profile.philosophy = philosophy
            profile.availability = availability
            profile.save()


            existing_awards = {str(award.id): award for award in awards}  # Store awards by ID
            deleted_awards = request.POST.get("deleted_awards", "").split(",")

            award_ids = request.POST.getlist("award_id")
            award_titles = request.POST.getlist("award_title")

            # Delete marked awards
            for award_id in deleted_awards:
                if award_id and award_id in existing_awards:
                    existing_awards[award_id].delete()

            for i, title in enumerate(award_titles):
                title = title.strip()
                if title:
                    if i < len(award_ids) and award_ids[i] in existing_awards:
                        # Update existing award
                        award = existing_awards[award_ids[i]]
                        award.title = title
                        file_key = f"award_file_{award.id}"
                        
                        if file_key in request.FILES:
                            award.file = request.FILES[file_key]  # Only update file if new one is provided
                            
                        award.save()
                    else:
                        # Create new award
                        new_file = request.FILES.get("award_file")  # Ensure new file is attached
                        if new_file:
                            TeacherAward.objects.create(teacher=teacher, title=title, file=new_file)

            messages.success(request, "Profile updated successfully.")
            return redirect("tech_setting")

        return render(request, "tech_setting.html", {"teacher": teacher, "profile": profile, "awards": awards,'settings':settings,"payments": payments,"total_amount_due": total_amount_due,'teacher_notifications':teacher_notifications})
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')


#used to tract the notification detail
@login_required
def update_teacher_notifications(request):

    try:
        teacher = Teacher.objects.get(user=request.user)
        settings, created = TeacherNotificationSettings.objects.get_or_create(teacher=teacher)

        if request.method == "POST":
            settings.email_notifications = request.POST.get("email_notifications") == "on"
            # settings.deletion_notifications = request.POST.get("deletion_notifications") == "on"
            # settings.mobile_notifications = request.POST.get("mobile_notifications") == "on"
            settings.auth_notifications = request.POST.get("auth_notifications") == "on"
            # settings.course_notifications = request.POST.get("course_notifications") == "on"
            
            settings.save()
            return JsonResponse({"success": True, "message": "Notification settings updated."})
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')

#used to make payment to educonnect
@login_required
def mark_payment_paid(request, payment_id):
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')
    try:
        teacher= Teacher.objects.get(user=request.user)
        if request.method == "POST":
            payment = get_object_or_404(TeacherPayment, id=payment_id, teacher=teacher)
            if payment.status == "pending":
                payment.mark_as_paid()
                return JsonResponse({"success": True, "new_status": "Paid", "update_date": payment.update_date.strftime("%Y-%m-%d %H:%M")})
            return JsonResponse({"success": False, "error": "Already paid"})
        return JsonResponse({"success": False, "error": "Invalid request"})
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')
    


#used for account security
@login_required
def update_teacher_profile(request):
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')
    context={}
    try:
        teacher = Teacher.objects.get(user=request.user)  # Use the logged-in teacher
        profile, created = TeacherProfile.objects.get_or_create(teacher=teacher)

        if request.method == "POST":
            # username = request.POST.get("username", "").strip()
            public_visibility = request.POST.get("public_visibility") == "true"
            # two_factor_auth = request.POST.get("two_factor_auth") == "true"
            deactivate_account = request.POST.get("deactivate_account") == "true"
            # current_password  = request.POST.get("pass").strip()
            # new_password = request.POST.get('new_pass').strip()

            profile.public_visibility = public_visibility
            # profile.two_factor_auth = two_factor_auth

            # Handle account deactivation
            teacher.status = "Inactive" if deactivate_account else "Active"

            # Save changes
            teacher.save()
            profile.save()
            messages.success(request, "setting change successfully")
            return redirect(request.path)
        
        return redirect("tech_setting")
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')


#used to feedback
@login_required
def submit_teacher_feedback(request):
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')
    try:
        context = {}
        teacher = Teacher.objects.get(user=request.user)
        if request.method == "POST":
            teacher = teacher  # Assuming user is authenticated and linked to a Teacher model
            category = request.POST.get("feedbackTitle")
            custom_category = request.POST.get("customTitle", "") if category == "Other" else ""
            feedback_text = request.POST.get("feedbackInput")
            rating = request.POST.get('rating') if request.POST.get('rating') else 1
            suggestions = request.POST.get("suggestions", "")
            file = request.FILES.get("upload")
            

            if not category or not feedback_text or not rating:
                context['message'] = 'all field are required'

            feedback = TeacherFeedback.objects.create(
                teacher=teacher,
                category=category,
                custom_category=custom_category,
                feedback_text=feedback_text,
                rating=rating,
                suggestions=suggestions,
                file=file,
            )
            
            messages.success(request, "Feedback submitted successfully!")
            return redirect(request.path)
        return redirect("tech_setting")
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')
    

#used to download data
@login_required
def generate_teacher_pdf(request, teacher_id):
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')
    try:
        # check_tech = Teacher.objects.get(user=request.user)
        teacher = Teacher.objects.get(user=request.user)
        profile = teacher.profile if hasattr(teacher, 'profile') else None
        course = Course.objects.filter(teacher=teacher)
        awards = teacher.teacher_award.all()
        payments = teacher.payments_made.all()
        feedbacks = TeacherFeedback.objects.filter(teacher=teacher)
        queries = StudentQuery.objects.filter(course__in=teacher.posts.values_list('course', flat=True))
        posts = teacher.posts.all()
        comments = Comment.objects.filter(post__in=posts)
        notifications = teacher.notification_settings if hasattr(teacher, 'notification_settings') else None
        teacher_payments = teacher.payments.all()

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{teacher.first_name}_{teacher.last_name}_data.pdf"'

        pdf = canvas.Canvas(response, pagesize=letter)
        pdf.setTitle(f"{teacher.first_name} {teacher.last_name} - Data Report")

        y_position = 750
        line_spacing = 20  
        page_width = 550  
        max_lines_per_page = 3  

        def draw_wrapped_text(pdf, text, x, y):
            lines = simpleSplit(text, "Helvetica", 12, page_width - x)
            for line in lines:
                pdf.drawString(x, y, line)
                y -= line_spacing
            return y  

        def check_page_space(pdf, y, min_required_space=60):
            """Checks if there's enough space on the current page, if not, creates a new page."""
            if y < min_required_space:
                pdf.showPage()
                pdf.setFont("Helvetica", 12)
                return 750  
            return y

        # Header
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(200, y_position, f"Teacher Report - {teacher.first_name} {teacher.last_name}")
        pdf.line(50, y_position - 10, 550, y_position - 10)
        y_position -= 30

        pdf.setFont("Helvetica", 12)

        # Basic Teacher Info
        y_position = draw_wrapped_text(pdf, f"Name: {teacher.first_name} {teacher.last_name}", 50, y_position)
        y_position = draw_wrapped_text(pdf, f"Email: {teacher.user.email}", 50, y_position)
        y_position = draw_wrapped_text(pdf, f"Phone: {teacher.phone_number or 'N/A'}", 50, y_position)
        y_position = draw_wrapped_text(pdf, f"Address: {teacher.address or 'N/A'}, {teacher.city or ''}", 50, y_position)
        y_position -= 10

        # Profile Information
        if profile:
            y_position = check_page_space(pdf, y_position)
            pdf.setFont("Helvetica-Bold", 12)
            y_position = draw_wrapped_text(pdf, "Profile Information:", 50, y_position)
            pdf.setFont("Helvetica", 12)
            y_position = draw_wrapped_text(pdf, f"Qualifications: {profile.qualifications or 'N/A'}", 50, y_position)
            y_position = draw_wrapped_text(pdf, f"Experience: {profile.experience_years or 'N/A'} years", 50, y_position)
            y_position = draw_wrapped_text(pdf, f"Specializations: {profile.specializations or 'N/A'}", 50, y_position)
            y_position -= 10

        # Awards
        if awards.exists():
            y_position = check_page_space(pdf, y_position)
            pdf.setFont("Helvetica-Bold", 12)
            y_position = draw_wrapped_text(pdf, "Awards:", 50, y_position)
            pdf.setFont("Helvetica", 12)
            for award in awards:
                y_position = draw_wrapped_text(pdf, f"- {award.title}", 50, y_position)
                y_position = check_page_space(pdf, y_position)
            y_position -= 10

        # Payments
        if payments.exists():
            y_position = check_page_space(pdf, y_position)
            pdf.setFont("Helvetica-Bold", 12)
            y_position = draw_wrapped_text(pdf, "Payments Made:", 50, y_position)
            pdf.setFont("Helvetica", 12)
            for payment in payments:
                y_position = draw_wrapped_text(pdf, f"- {payment.course.title}: ${payment.amount} on {payment.payment_date}", 50, y_position)
                y_position = check_page_space(pdf, y_position)
            y_position -= 10

        #course
        if course.exists():
            y_position = check_page_space(pdf, y_position)
            pdf.setFont("Helvetica-Bold", 12)
            y_position = draw_wrapped_text(pdf, "Course Created:", 50, y_position)
            pdf.setFont("Helvetica", 12)
            for course in course:
                y_position = draw_wrapped_text(pdf, f"- {course.title[:80]}:- {course.description[:100]}... total student enroll: ({course.enroll}/{course.max_enrollments})", 50, y_position)
                y_position = check_page_space(pdf, y_position)
            y_position -= 10

        # Feedback
        if feedbacks.exists():
            y_position = check_page_space(pdf, y_position)
            pdf.setFont("Helvetica-Bold", 12)
            y_position = draw_wrapped_text(pdf, "Feedback Received:", 50, y_position)
            pdf.setFont("Helvetica", 12)
            for feedback in feedbacks:
                y_position = draw_wrapped_text(pdf, f"- {feedback.category}: {feedback.feedback_text[:100]}... ({feedback.rating}/5)", 50, y_position)
                y_position = check_page_space(pdf, y_position)
            y_position -= 10

        # Comments
        if comments.exists():
            y_position = check_page_space(pdf, y_position)
            pdf.setFont("Helvetica-Bold", 12)
            y_position = draw_wrapped_text(pdf, "Comments on Posts:", 50, y_position)
            pdf.setFont("Helvetica", 12)
            for comment in comments:
                y_position = draw_wrapped_text(pdf, f"-{comment.course[:100]} {comment.content[:100]}... ({comment.created_at.date()})", 50, y_position)
                y_position = check_page_space(pdf, y_position)
            y_position -= 10

        # Notification Settings
        if notifications:
            y_position = check_page_space(pdf, y_position)
            pdf.setFont("Helvetica-Bold", 12)
            y_position = draw_wrapped_text(pdf, "Notification Settings:", 50, y_position)
            pdf.setFont("Helvetica", 12)
            y_position = draw_wrapped_text(pdf, f"Email Notifications: {'Enabled' if notifications.email_notifications else 'Disabled'}", 50, y_position)
            y_position = draw_wrapped_text(pdf, f"Deletion Notifications: {'Enabled' if notifications.mobile_notifications else 'Disabled'}", 50, y_position)
            y_position = draw_wrapped_text(pdf, f"Auth Notifications: {'Enabled' if notifications.auth_notifications else 'Disabled'}", 50, y_position)
            y_position = draw_wrapped_text(pdf, f"Course Notifications: {'Enabled' if notifications.course_notifications else 'Disabled'}", 50, y_position)
            y_position -= 10


        pdf.showPage()
        pdf.save()
        return response
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')
    
