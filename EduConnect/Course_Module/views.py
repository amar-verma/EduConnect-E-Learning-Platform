import datetime
from datetime import datetime
import json
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.http import urlencode
from django.http import Http404, HttpResponse, JsonResponse
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now
from .forms import CourseCommentForm,StudentRegistrationForm
from EduAssessment.models import Enrollment
from Students.models import SearchQuery, Student,StudentNotificationSettings,StudentProfile,Payment,StudentNotificationDashboard,TeacherNotificationDashBoard
from .models import Assignment, AssignmentSubmission, Certificate, Course, Content,EdUContent, EduOTP,EduSupport,EduFeed,EduForm,CourseComment,CourseFeatures,CourseLearning,CourseSkills,AdvertisementSmall,AdsPic, StudentProgress
from Teachers.models import Comment, Post, ReceivedPayment, StudentQuery, Teacher,TeacherAward,TeacherProfile
from django.db.models import OuterRef, Subquery
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
import imgkit
import base64
from django.core.files.base import ContentFile
import os
import random
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.conf import settings
from Edu_Main.models import User
from django.shortcuts import render
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
import json
from itertools import zip_longest
from django.db.models import Q
from django.db.models import F
from django.urls import reverse
import razorpay
from razorpay.errors import BadRequestError
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from difflib import get_close_matches






def home(request):
    # Step 1: Fetch courses for each category while avoiding duplication
    try:
        programming_ids = Course.objects.filter(category='Programming Language', is_display=True, id__isnull=False).order_by('-rating')[:6].values_list('id', flat=True)
        database_ids = Course.objects.filter(category='Database Design',is_display=True, id__isnull=False).exclude(id__in=programming_ids).order_by('-rating')[:6].values_list('id', flat=True)
        nocode_ids = Course.objects.filter(category='No-Code Development',is_display=True, id__isnull=False).exclude(id__in=programming_ids).exclude(id__in=database_ids).order_by('-rating')[:6].values_list('id', flat=True)
        other_ids = Course.objects.filter(category='Other',is_display=True, id__isnull=False).exclude(id__in=programming_ids).exclude(id__in=database_ids).exclude(id__in=nocode_ids).order_by('-rating')[:6].values_list('id', flat=True)

        programming = Course.objects.filter(id__in=programming_ids).values('title', 'duration', 'enroll', 'course_img')
        database = Course.objects.filter(id__in=database_ids).values('title', 'duration', 'enroll', 'course_img')
        nocode = Course.objects.filter(id__in=nocode_ids).values('title', 'duration', 'enroll', 'course_img')
        other = Course.objects.filter(id__in=other_ids).values('title', 'duration', 'enroll', 'course_img')

        # Serialize the data into JSON with URLs for images (no need for .url)
        context = {
            'programming': [
                {
                **course,
                'course_img': request.build_absolute_uri(settings.MEDIA_URL +course['course_img']) if course['course_img'] else None
                } for course in programming
            ],
            'database': [
                {
                **course,
                'course_img': request.build_absolute_uri(settings.MEDIA_URL +course['course_img']) if course['course_img'] else None
                } for course in database
            ],
            'nocode': [
                {
                **course,
                'course_img': request.build_absolute_uri(settings.MEDIA_URL +course['course_img']) if course['course_img'] else None
                } for course in nocode
            ],
            'other': [
                {
                **course,
                'course_img': request.build_absolute_uri(settings.MEDIA_URL +course['course_img']) if course['course_img'] else None
                } for course in other
            ],
        }
        

        # Pass context to the template
        return render(request, 'home.html', {'courses_json': json.dumps(context, cls=DjangoJSONEncoder)})
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('std_login')

def about_us(request):
    return render(request, 'co-operatetraining.html')

def join_us(request):
    context={}
    feed = EduFeed.objects.all()[:2]

    if request.method == 'POST':
        # Retrieve form data
        try:
            name = request.POST.get('name')
            email = request.POST.get('email')
            desc = request.POST.get('company')  # 'company' holds skills and details
            country_code = request.POST.get('country_code')
            mobile = request.POST.get('mobile')

            # Combine country code and mobile number
            full_mobile = f"{country_code}{mobile}"

            # Validate if the email or mobile number already exists
            if EduForm.objects.filter(mail_id=email).exists():
                context['message'] = 'This email is already registered.'
            elif EduForm.objects.filter(m_no=full_mobile).exists():
                context['message'] = 'This mobile number is already registered.'
            else:
                form_data = EduForm(name=name, description=desc, mail_id=email, m_no=full_mobile)
                form_data.save()
                context['message'] = 'Your details have been successfully submitted!'
        except Exception as e:
            context['message'] = 'Something Went Wrong, Please try again'

    context['feed'] = feed
    
    return render(request, 'hirejob.html',context)


def CourseDetail(request):
    return render(request, 'courseDetail.html')



def homeCard(request, cname):
    context = {}
    name = ''
    COURSE_DATA = {
    'Web_Development': {
        'map': 'Web Development',
        'whoCan': 'Executive Post Graduate Certification in Programming Languages and Software Development',
        'title': 'Full Stack Web Development: Build Modern, Scalable Websites',
        'body': 'Learn both front-end and back-end technologies to design, develop, and deploy dynamic websites and web applications.',
        'image': 'web.jpeg',
    },
    'Data_Science': {
        'map': 'Data Science',
        'whoCan': 'Advanced Certification in Data Science',
        'title': 'Advanced Certification in Data Science',
        'body': 'Advanced Certification in Data Science',
        'image': 'course_img1.jpg',
    },
    'Programming_Language': {
        'map': 'Programming Language',
        'whoCan': 'Post Graduate Certification in Programming languages',
        'title': 'Post Graduate Certification in Python Programming',
        'body': 'Post Graduate Certification in Python Programming',
        'image': 'course_img12.jpg',
    },
    'Game_Development': {
        'map': 'Game Development',
        'whoCan': 'Game Development Certification Program',
        'title': 'Game Development Certification Program',
        'body': 'Learn to build immersive gaming experiences with industry-leading game development tools.',
        'image': 'course_img9.jpg',
    },
    'Mobile_Development': {
        'map': 'Mobile Development',
        'whoCan': 'Mobile App Development Professional Course',
        'title': 'Mobile App Development Professional Course',
        'body': 'Develop high-performance mobile apps with cutting-edge mobile development frameworks.',
        'image': 'course_img8.jpg',
    },
    'Database_Design': {
        'map': 'Database Design',
        'whoCan': 'Database Design and Management Certification',
        'title': 'Database Design and Management Certification',
        'body': 'Master database design and management techniques with practical case studies.',
        'image': 'course_img11.jpg',
    },
    'Software_Testing': {
        'map': 'Software Testing',
        'whoCan': 'Software Testing Professional Certification',
        'title': 'Software Testing Professional Certification',
        'body': 'Learn manual and automated software testing to ensure high-quality software products.',
        'image': 'course_img7.jpg',
    },
    'Software_Engineering': {
        'map': 'Software Engineering',
        'whoCan': 'Software Engineering Professional Program',
        'title': 'Software Engineering Professional Program',
        'body': 'Gain expertise in software engineering principles, design patterns, and architecture.',
        'image': 'course_img5.jpg',
    },
    'Software_Development_Tools': {
        'map': 'Software Development Tools',
        'whoCan': 'Software Development Tools Mastery Program',
        'title': 'Software Development Tools Mastery Program',
        'body': 'Become proficient in essential development tools like Git, Docker, and more.',
        'image': 'course_img3.jpg',
    },
    'No_Code_Development': {
        'map': 'No-Code Development',
        'whoCan': 'No-Code Development Professional Course',
        'title': 'No-Code Development Professional Course',
        'body': 'Learn to build powerful applications without coding using top no-code platforms.',
        'image': 'course_img6.jpg',
    },
    'Other': {
        'map': 'Other',
        'whoCan': 'Specialized Certification Programs',
        'title': 'Specialized Certification Programs',
        'body': 'Explore various specialized certification programs tailored to your career goals.',
        'image': 'course_img4.jpg',
    }

    }

    course_details = COURSE_DATA.get(cname)
    # If cname is not in the dictionary, raise an error or handle it
    if not course_details:
        return render(request, '404.html', context)
    edu_content = EdUContent.objects.filter(course__title=course_details['whoCan'])
    

    educard1 = Course.objects.filter(category=course_details['map'],is_display=True, id__isnull=False).order_by('-rating')
    educard2 = Course.objects.filter(category=course_details['map'],is_display=True, id__isnull=False).order_by('-enroll')


    
    top_courses_per_teacher = (
        Course.objects.filter(
            teacher=OuterRef('teacher'), 
            category=course_details['map'],
        )
        .order_by('-rating')
        .values('id')[:1]
    )
    unique_teacher_courses = (
        Course.objects.filter(
            id__in=Subquery(top_courses_per_teacher)
        )
        .order_by('-rating')[:3]  # Get the top 3 unique teacher courses
    )

    edutech = unique_teacher_courses
    if request.method == "POST":
        try:
            # Extract data from the form submission
            name = request.POST.get("name")
            mail_id = request.POST.get("mail_id")
            country_code = request.POST.get("country_code")
            mobile = request.POST.get("mobile")

            # Concatenate country code and mobile number
            mobile_no = f"{country_code}{mobile}"

            # Validate required fields
            if not name or not mail_id or not mobile_no:
                return JsonResponse({"error": "All fields are required."}, status=400)

            # Save feedback data
            EduSupport.objects.create(
                name=name,
                mail_id=mail_id,
                num=mobile_no,
                from_pg=f"page: {course_details['map']}"
            )

            context['message'] = 'Your response has been submitted, thank you! we will reached you soon'
        except Exception as e:
            context['message'] = 'somthing went wrong, please try again later.'

    context['eduCard1'] = educard1
    context['eduCard2'] = educard2
    context['edu_content'] = edu_content
    context['eduCourse'] = course_details
    context['eduTech'] = edutech
   
    
    return render(request, 'homeCard.html', context)




def course_detail(request, course_id):
    context = {}
    course = get_object_or_404(Course, id=course_id)
    if not course.is_display:
        messages.error(request, 'This course is not available.')
        return redirect('/')
    try:
        courses = Course.objects.get(id=course_id)
        content = list(Content.objects.filter(course=course).order_by('order')[:3])
        content_titles = list(Content.objects.filter(course=course).order_by('order').values_list('title', flat=True))
        combined_content = zip_longest(content_titles, content, fillvalue=None)
        comment = CourseComment.objects.filter(course=courses)
        print(comment)
        features = CourseFeatures.objects.filter(course=course)
        learning = CourseLearning.objects.filter(course=course)
        skills = CourseSkills.objects.filter(course=course)
        Ads = AdvertisementSmall.objects.filter(is_active=True, start_date__lte=datetime.now(), end_date__gte=datetime.now())[:1]
        related_courses = Course.objects.filter(category=course.category, is_display=True)[:10]
        other_course = related_courses 
        if len(related_courses) < 10:
            additional_courses = Course.objects.filter(Q(is_display=True) & Q(category__isnull=False)).exclude(id__in=[course.id for course in related_courses]).order_by('-rating')[:10 - len(related_courses)] 
            other_course = list(related_courses) + list(additional_courses)
            context['other_course']= other_course

        login_status = False
        course_max = False
        if course.enroll >= course.max_enrollments:
            course_max = True
        else:
            course_max = False

        if request.user.is_authenticated and request.user.user_type == 'student':
            try:
                student = get_object_or_404(Student, user=request.user)
                if Enrollment.objects.filter(student=student, course=course).exists():
                    login_status = True
            except Exception as e:
                print(f"An error occurred: {e}")

        context['courses'] = courses
        if course and features and learning and skills:
            context['content'] = content  # Top 3 items with full details
            context['content_titles'] = content_titles
            context['combined_content'] = combined_content
            context['comment'] = comment
            context['features'] = features
            context['learning'] = learning
            context['skills'] = skills
            context['ads'] = Ads
            context['other_course'] = other_course
            context['course_id'] = course_id
            context['login_status'] = login_status
            context['course_max'] = course_max
            return render(request, 'courseDetail.html', context)
        else:
            return render(request, '404.html')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('/')
    

@login_required
def confirm_enrollment(request, course_id):
    context={}
    # Check if user is a student
    if request.user.user_type != 'student':
        messages.error(request, "Only students can enroll in courses.")
        return redirect('/')
    try:
        student = get_object_or_404(Student, user=request.user)
        course = get_object_or_404(Course, id=course_id)

        if not course.is_display:
            messages.error(request, 'This course is not available.')
            return redirect('/')

        # Check if already enrolled
        if Enrollment.objects.filter(student=student, course=course).exists():
            messages.info(request, "You are already enrolled in this course.")
            return redirect('course_detail', course_id=course.id)

        # if request.method == "POST":
        #     # If user clicks "Yes", proceed to payment
        #     if 'confirm' in request.POST:
        #         return redirect('process_payment', course_id=course.id)  
        #     else:
        #         messages.info(request, "Enrollment canceled.")
        #         return redirect('course_detail', course_id=course.id)

        context['student'] = student
        context['course'] = course
        pay_id = str(random.randrange(1000,9999))
        # sum = course.price
        sum = course.price
        context['sum'] = sum
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            data = { "amount": sum * 100, "currency": "INR", "receipt": pay_id } 
            payment = client.order.create(data=data)
            context['payment'] = payment
        except BadRequestError as e:
            context['error'] = "There was an error processing your payment. Please try again."


        return render(request, 'confirm_enrollment.html', context)
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('/')
    


@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        payment_id = request.POST.get('payment_id')
        order_id = request.POST.get('order_id','Test123')
        signature = request.POST.get('signature','')
        student_id = request.POST.get('student_id') 
        course_id = request.POST.get('course_id') 
        amount = request.POST.get('amount')   


        # Verify the payment signature
        # params = {
        #     'razorpay_order_id': order_id,
        #     'razorpay_payment_id': payment_id,
        #     'razorpay_signature': signature
        # }

        try:
            # Verifying the payment signature with Razorpay
            # client.utility.verify_payment_signature(params)
            
            # Fetch the student and course from the database using the IDs
            student = Student.objects.get(student_id=student_id)
            course = Course.objects.get(id=course_id)
            if not course.is_display:
                messages.error(request, 'This course is not available.')
                return redirect('/')
            teacher_course = course.teacher  # Assuming teacher is linked to course
            teacher_email = teacher_course.user.email

            
            # Payment is successful, handle the payment here
            payment = Payment.objects.create(
                payment_id=payment_id,
                order_id=order_id,
                student=student,  # Store student reference
                course=course,    # Store course reference
                payment_status='success',
                amount=request.POST.get('amount'),
            )

            enrollment = Enrollment.objects.create(
                student=student,
                course=course,
            )
            received_payment = ReceivedPayment.objects.create(
                student=student,
                course=course,
                amount=request.POST.get('amount')
            )

            course.enroll += 1  
            course.save()

            student_message = f"Congratulations {student.user.first_name}, you have successfully enrolled in {course.title}."
            student_notification = StudentNotificationDashboard.objects.create(
                student=student,
                message=student_message
            )
            
            # Create the notification for the teacher
            teacher_message = f"New student enrolled: {student.user.first_name} in your course {course.title}."
            teacher_notification = TeacherNotificationDashBoard.objects.create(
                teacher=teacher_course,
                message=teacher_message
            )


            # Send a confirmation email to the student
            subject = f"Enrollment Confirmation for {course.title}"
            message = f"Dear {student.user.first_name},\n\nYou have successfully enrolled in the course: {course.title}.\n\nThank you for choosing our platform!"
            message1 = f"Dear {teacher_course.first_name},\n\n {student.user.first_name} successfully enrolled your the course: {course.title}.\n\nThank you for choosing our platform!"

            recipient_list = [student.user.email]
            recipient_list1 = [teacher_email]

            # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
            # send_mail(subject, message1, settings.DEFAULT_FROM_EMAIL, recipient_list1)

            return redirect('enroll_course', course_id=course_id)

        except razorpay.errors.SignatureVerificationError:
            # If signature verification fails, mark payment as failed
            return JsonResponse({'status': 'failure', 'message': 'Payment signature verification failed'})

    return JsonResponse({'status': 'failure', 'message': 'Invalid request'}, status=400)


@login_required
def enroll_course(request, course_id):
    if not request.user.is_authenticated or request.user.user_type != 'student': 
        messages.error(request, "You must be a student to access this page.")
        return redirect('std_login')

    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, "Student login not found.")
        return redirect('std_login')
    
    try:
        course = get_object_or_404(Course, id=course_id)
        content_list = Content.objects.filter(course=course).order_by('id')

        # Ensure student is enrolled
        if not Enrollment.objects.filter(student=student, course=course).exists():
            return redirect('/')

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

        # Get all assignment submissions for this student in this course
        all_assignments = Assignment.objects.filter(question__in=content_list)
        
        # Get all submissions for this student in this course
        all_submissions = AssignmentSubmission.objects.filter(
            student=student, 
            assignment__question__in=content_list
        ).select_related('assignment')
        
        # Get filter parameter
        submission_filter = request.GET.get('filter', 'all')
        
        # Apply filter
        if submission_filter == 'pending':
            filtered_submissions = all_submissions.filter(status='pending')
        elif submission_filter == 'completed':
            filtered_submissions = all_submissions.filter(status='completed')
        elif submission_filter == 'rework':
            filtered_submissions = all_submissions.filter(status='rework')
        else:
            filtered_submissions = all_submissions
        
        # Count submissions by status
        pending_count = all_submissions.filter(status='pending').count()
        completed_count = all_submissions.filter(status='completed').count()
        rework_count = all_submissions.filter(status='rework').count()
        
        # Check if certificate is generated
        certificate_generated = Certificate.objects.filter(student=student, course=course).exists()

        context = {
            "course": course,
            "content_list": content_list,
            "progress_percentage": progress_percentage,
            "total_contents": total_contents,
            "completed_contents": completed_contents,
            "total_assignments": total_assignments,
            "submitted_assignments": submitted_assignments,
            "course_id": course_id,
            "rejected_assignments": filtered_submissions.filter(status="rework"),
            "rejected_assignemtn_count": rework_count,
            "all_submissions": filtered_submissions,
            "submission_counts": {
                "pending": pending_count,
                "completed": completed_count,
                "rework": rework_count,
                "total": all_submissions.count()
            },
            "current_filter": submission_filter,
            "certificate_generated": certificate_generated,
        }
        return render(request, 'enroll_course.html', context)
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('std_dashboard')



@login_required
def enroll_course_content(request, course_id, content_id):
    if not request.user.is_authenticated or request.user.user_type != 'student': 
        messages.error(request, "You must be a student to access this page.")
        return redirect('std_login')

    try:
        student = Student.objects.get(user=request.user)

    except Student.DoesNotExist:
        messages.error(request, "Student login not found.")
        return redirect('std_login')
    try:
        course = get_object_or_404(Course, id=course_id)
        content = get_object_or_404(Content, id=content_id, course=course)

        # Fetch course contents
        content_list = list(Content.objects.filter(course=course).order_by('id'))

        # Fetch assignments and submissions for the current content
        assignments = Assignment.objects.filter(question=content)
        submissions = AssignmentSubmission.objects.filter(student=student, assignment__in=assignments)

        # Get completed content count
        completed_content = StudentProgress.objects.filter(student=student, content__in=content_list, is_completed=True).count()

        # Get total assignments count
        total_assignments = Assignment.objects.filter(question__in=content_list).count()

        # Get submitted assignments count
        submitted_assignments = AssignmentSubmission.objects.filter(student=student, assignment__question__in=content_list).count()

        # Calculate total points
        total_pages = len(content_list)  # 1 point per page
        total_points = total_pages + (total_assignments * 2)  # Each assignment = 2 points
        completed_points = completed_content + (submitted_assignments * 2)

        # Compute progress percentage
        progress_percentage = (completed_points / total_points) * 100 if total_points else 0
        progress_percentage = min(100, round(progress_percentage, 2))  # Ensure max 100%

        # Determine next and previous content
        current_index = content_list.index(content) if content in content_list else None
        prev_content = content_list[current_index - 1] if current_index and current_index > 0 else None
        next_content = content_list[current_index + 1] if current_index is not None and current_index < len(content_list) - 1 else None

        # Ensure next_content is None if on last content
        if current_index == len(content_list) - 1:
            next_content = None

        # Restrict access if previous content is not completed
        if prev_content:
            prev_progress = StudentProgress.objects.filter(student=student, content=prev_content).first()
            prev_assignments = Assignment.objects.filter(question=prev_content)
            prev_submissions = AssignmentSubmission.objects.filter(student=student, assignment__in=prev_assignments)

            # Ensure previous content is marked as completed
            prev_completed = prev_progress and prev_progress.is_completed
            all_prev_assignments_submitted = prev_assignments.count() == prev_submissions.count()

            if not prev_completed or (prev_assignments.exists() and not all_prev_assignments_submitted):
                return redirect('enroll_course_content', course_id=course.id, content_id=prev_content.id)

        # Mark current content as completed only if all assignments are submitted
        if assignments.count() == submissions.count():
            progress, created = StudentProgress.objects.get_or_create(student=student, content=content)
            progress.is_completed = True
            progress.save()

        context = {
            "course": course,
            "content": content,
            "content_list": content_list,
            "assignments": assignments,
            "submissions": submissions,
            "prev_content": prev_content,
            "next_content": next_content,
            "progress_percentage": progress_percentage,
            'course_id':course_id
        }
        return render(request, 'enroll_course_page.html', context)
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('std_dashboard')



@login_required
def submit_assignment(request, assignment_id):
    if not request.user.is_authenticated or request.user.user_type != 'student': 
        messages.error(request, "You must be a student to access this page.")
        return redirect('std_login')

    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, "Student login not found.")
        return redirect('std_login')
    try:
        assignment = get_object_or_404(Assignment, id=assignment_id)

        if request.method == "POST" and request.FILES.get('file'):
            file = request.FILES['file']
            submission = AssignmentSubmission.objects.filter(student=student, assignment=assignment).first()

            if submission:
                submission.file = file
                submission.status = 'pending'
                submission.save()
            else:
                AssignmentSubmission.objects.create(student=student, assignment=assignment, file=file)


            # Mark assignment as completed in StudentProgress
            progress, created = StudentProgress.objects.get_or_create(student=student, content=assignment.question)
            progress.assignment_submitted = True
            progress.save()

        return redirect('enroll_course_content', course_id=assignment.question.course.id, content_id=assignment.question.id)
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('std_dashboard')



from django.contrib import messages
@login_required
def course_feedback(request, course_id):
    if not request.user.is_authenticated or request.user.user_type != 'student': 
        messages.error(request, "You must be a student to access this page.")
        return redirect('std_login')

    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, "Student login not found.")
        return redirect('std_login')
    
    try:
        course = get_object_or_404(Course, id=course_id)

        # Check if the student is enrolled
        enrollment = Enrollment.objects.filter(student=student, course=course).exists()
        if not enrollment:
            return redirect('/')  # Redirect if not enrolled or not completed

        # Check if all content is completed and all assignments are submitted
        content_list = Content.objects.filter(course=course)
        total_contents = content_list.count()
        completed_contents = StudentProgress.objects.filter(student=student, content__in=content_list, is_completed=True).count()
        
        total_assignments = Assignment.objects.filter(question__in=content_list).count()
        submitted_assignments = AssignmentSubmission.objects.filter(student=student, assignment__question__in=content_list, status='completed').count()
        
        total_contents = content_list.count()  # Each content = 1 point
        total_assignments = Assignment.objects.filter(question__in=content_list).count()  # Each assignment = 2 points
        total_possible_points = (total_contents * 1) + (total_assignments * 2)

        # Calculate earned points by student
        completed_contents = StudentProgress.objects.filter(student=student, content__in=content_list, is_completed=True).count()
        submitted_assignments = AssignmentSubmission.objects.filter(student=student, assignment__question__in=content_list).count()
        earned_points = (completed_contents * 1) + (submitted_assignments * 2)

        # Compute progress percentage
        progress_percentage = (earned_points / total_possible_points) * 100 if total_possible_points > 0 else 0
        progress_percentage = round(progress_percentage, 2)

        if completed_contents < total_contents or submitted_assignments < total_assignments:
            messages.info(request,'please complete all the assignments and chapter first')
            return redirect('enroll_course', course_id)  # Redirect if all requirements are not met

        if request.method == "POST":
            comment_text = request.POST.get('comment')
            value = request.POST.get('respo') == 'true'  # True if liked, False otherwise

            CourseComment.objects.update_or_create(
                course=course,
                name=student.first_name + " " + student.last_name,  # Assuming Student model has a linked User
                photo=student.profile_picture,  # Assuming student has a profile picture field
                comment=comment_text,
                value=value
            )
            return redirect('course_detail', course_id=course.id)

        return render(request, 'enroll_feedback.html', {'course': course,'course_id':course_id,'content_list':content_list,"progress_percentage": progress_percentage})
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('std_dashboard')


@login_required
def enroll_certificate(request, course_id):
    if not request.user.is_authenticated or request.user.user_type != 'student': 
        messages.error(request, "You must be a student to access this page.")
        return redirect('std_login')

    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, "Student login not found.")
        return redirect('std_login')
    context = {}

    course = get_object_or_404(Course, id=course_id)

    try:
        enrollment = Enrollment.objects.get(student=student, course=course)
    except Enrollment.DoesNotExist:
        messages.error(request, "You are not enrolled in this course.")
        return redirect('/')  
    
    try:
        certification = Certificate.objects.get(student=student, course=course)
        certificate_exists = True
    except Certificate.DoesNotExist:
        certification = None
        certificate_exists = False
        messages.info(request, 'Your certificate is not generated yet. Please make sure to complete the course and ask your instructor.')
        return redirect('enroll_course', course_id)

    # Check if all content is completed and all assignments are submitted
    content_list = Content.objects.filter(course=course)
    total_contents = content_list.count()
    completed_contents = StudentProgress.objects.filter(student=student, content__in=content_list, is_completed=True).count()
    
    total_assignments = Assignment.objects.filter(question__in=content_list).count()
    submitted_assignments = AssignmentSubmission.objects.filter(student=student, assignment__question__in=content_list, status='completed').count()
    
    total_contents = content_list.count()  # Each content = 1 point
    total_assignments = Assignment.objects.filter(question__in=content_list).count()  # Each assignment = 2 points
    total_possible_points = (total_contents * 1) + (total_assignments * 2)

    # Calculate earned points by student
    completed_contents = StudentProgress.objects.filter(student=student, content__in=content_list, is_completed=True).count()
    submitted_assignments = AssignmentSubmission.objects.filter(student=student, assignment__question__in=content_list).count()
    earned_points = (completed_contents * 1) + (submitted_assignments * 2)

    # Compute progress percentage
    progress_percentage = (earned_points / total_possible_points) * 100 if total_possible_points > 0 else 0
    progress_percentage = round(progress_percentage, 2)

    enroll_id = f"{enrollment.id:04d}"
    course_id_no = f"{course_id:04d}"

    context={
        "student_name": student.first_name+" "+student.last_name ,
        "course_title": course.title,
        "professor_name": course.teacher.first_name+" "+course.teacher.last_name,
        "certificate_date": certification.created_at,
        "enroll_id": enroll_id,
        'course': course,
        'course_id':course_id,
        "course_id_no":course_id_no,
        'content_list':content_list,
        "progress_percentage": progress_percentage,

    }
    
    return render(request, 'enroll_certicate.html', context)


@login_required
def enroll_post_std(request, course_id):
    if not request.user.is_authenticated or request.user.user_type != 'student': 
        messages.error(request, "You must be a student to access this page.")
        return redirect('std_login')

    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, "Student login not found.")
        return redirect('std_login')
    try:
        course = get_object_or_404(Course, id=course_id)
        
        # Check if student is enrolled in the course
        if not Enrollment.objects.filter(student=student, course=course).exists():
            messages.error(request, "You are not enrolled in this course.")
            return redirect('/')
        
        # Get all posts for this course
        posts = Post.objects.filter(course=course).order_by('-created_at')
        
        # Get all queries for this student in this course
        queries = StudentQuery.objects.filter(student=student, course=course).order_by('-created_at')
        
        # Handle new query submission
        if request.method == 'POST':
            if 'query_text' in request.POST:
                query_text = request.POST.get('query_text')
                if query_text:
                    # Create new query
                    query = StudentQuery.objects.create(
                        student=student,
                        course=course,
                        query_text=query_text
                    )
                    
                    # Create notification for teacher
                    TeacherNotificationDashBoard.objects.create(
                        teacher=course.teacher,
                        message=f"New query from {student.first_name} {student.last_name} in course '{course.title}'"
                    )
                    
                    messages.success(request, "Your query has been sent to the instructor.")
                    return redirect('enroll_post_std', course_id=course_id)
            
            elif 'comment_content' in request.POST and 'post_id' in request.POST:
                comment_content = request.POST.get('comment_content')
                post_id = request.POST.get('post_id')
                
                try:
                    post = Post.objects.get(id=post_id, course=course)
                    
                    # Create new comment
                    Comment.objects.create(
                        post=post,
                        student=student,
                        content=comment_content
                    )
                    
                    messages.success(request, "Your comment has been added.")
                    return redirect('enroll_post_std', course_id=course_id)
                except Post.DoesNotExist:
                    messages.error(request, "The post you're trying to comment on doesn't exist.")
        
        context = {
            'course': course,
            'posts': posts,
            'queries': queries,
            'content_list': Content.objects.filter(course=course),
            'course_id': course_id,
        }
        
        return render(request, 'enroll_std_post.html', context)
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('std_dashboard')
    


# def std_otp(request):
#     pass

def explore_course(request):
    context = {}
    ads = AdsPic.objects.filter(is_active=True, start_date__lte=datetime.now(), end_date__gte=datetime.now())[:1]
    context['ads'] = ads
    return render(request,'explore.html',context)


def filter_courses(request):
    if request.method == 'GET':
        course = request.GET.get('category', 'all')
        sort_by = request.GET.get('sortBy', 'newest')
        price = request.GET.get('price', 'all')
        enrollment = request.GET.get('enrollment', 'all')
        rating = request.GET.get('rating', 'all')
        popularity = request.GET.get('popularity', 'all')

        if course == 'all':
            courses = Course.objects.filter(is_display=True)
        else:
            courses = Course.objects.filter(category=course,is_display=True)

        # Apply filters
        if price == 'all':
            courses = courses.filter(price__gte=0)
        elif price == 'free':
            courses = courses.filter(price=0)
        elif price == 'paid':
            courses = courses.filter(price__gt=0)

        if enrollment == 'all':
            courses = courses.filter(enroll__gte=0)
        if enrollment == 'available':
            courses = courses.filter(enroll__lt=F('max_enrollments'))
        elif enrollment == 'full':
            courses = courses.filter(enroll__gte=F('max_enrollments'))

        if rating == 'all':
            courses = courses.filter(rating__lte=5)
        elif rating == '5-stars':
            courses = courses.filter(rating=5)
        elif rating == '4-stars':
            courses = courses.filter(rating=4)
        elif rating == '3-stars':
            courses = courses.filter(rating=3)
        elif rating == '2-stars':
            courses = courses.filter(rating=2)
        elif rating == '1-stars':
            courses = courses.filter(rating=1)
        
        

        if sort_by == 'newest':
            courses = courses.order_by('-created_at')
        elif sort_by == 'oldest':
            courses = courses.order_by('created_at')

        # Add popularity-based filtering
        if popularity == 'all':
            courses = courses.filter(like__gte=0)
        elif popularity == 'most-liked':
            courses = courses.order_by('-like')
        
        # Convert courses to JSON
        course_data = list(courses.values('id', 'title', 'price', 'rating', 'like', 'enroll', 'course_img','max_enrollments','created_at','category'))
        # print(course_data)
        for course in course_data:
            course['course_img'] = f"{settings.MEDIA_URL}{course['course_img']}"
        for course in course_data:
            course['detail_url'] = reverse('course_detail', args=[course['id']])
        for course in course_data:
            course['created_at'] = course['created_at'].strftime('%Y-%m-%d')
        return JsonResponse({'courses': course_data}, safe=False)
    

def teacher_profile(request,teach_id):
    context = {}
    try:
        teacher_data = Teacher.objects.get(teacher_id=teach_id)
        courses = Course.objects.filter(teacher=teacher_data,is_display=True)
        courses2 = Course.objects.exclude(teacher=teacher_data,is_display=False).order_by('-rating')
        profile,created  = TeacherProfile.objects.get_or_create(teacher=teacher_data)
        hide_teacher = False
        if not profile.public_visibility:
            hide_teacher = True
        awards = TeacherAward.objects.filter(teacher=teacher_data)
        comments = CourseComment.objects.filter(course__teacher=teacher_data,value=True)[:3]
        context['teacher'] = teacher_data
        context['courses'] = courses
        context['courses2'] = courses2
        context['profile'] = profile
        context['awards'] = awards
        context['comments'] = comments
        context['hide_teacher'] = hide_teacher
        return render(request,'teacherprofile.html',context)
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('/')



def std_login(request):
    email_session = request.session.get("otp_email")
    if email_session:
        del request.session["otp_email"]

    img_dir = os.path.join(settings.BASE_DIR, 'static', 'img', 'std_auth')
    
    if not os.path.exists(img_dir):
        return render(request, 'login.html', {'auth_image': None})
    
    available_images = [img for img in os.listdir(img_dir) if img.endswith(('.png', '.jpg', '.jpeg'))]
    selected_image = random.choice(available_images) if available_images else None
    request.session['auth_image'] = selected_image

    return render(request,'login.html',{'auth_image': selected_image})

def send_otp(email,otp_type="verification"):
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



def verify_student_login(request):
    try:
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")
            verify = request.POST.get("verify") == "on"

            if not username or not password:
                messages.error(request, "Please fill in all details.")
                return redirect("std_login")

            auth_image = request.session.get("auth_image")

            # Authenticate user
            user = authenticate(request, username=username, password=password)
            
            if user is not None and user.user_type == 'student':
                try:
                    student = user.student
                    
                    if not student.profile_picture:
                        messages.error(request, "Profile picture is missing.")
                        return redirect("std_login")

                    student_image_name = os.path.basename(student.profile_picture.name)
                    notification_settings, created = StudentNotificationSettings.objects.get_or_create(student=student)

                    if verify:
                        if student_image_name == auth_image:
                            if notification_settings.auth_notifications:
                                otp = send_otp(user.email,otp_type="verification")
                                request.session["otp_email"] = user.email
                                return redirect("verify_otp")
                            else:
                                login(request, user)
                                return redirect("std_dashboard")
                        else:
                            messages.error(request, "Verification failed. Try again.")
                            return redirect("std_login")
                    else:
                        if student_image_name != auth_image:
                            if notification_settings.auth_notifications:
                                otp = send_otp(user.email,otp_type="verification")
                                request.session["otp_email"] = user.email
                                return redirect("verify_otp")
                            else:
                                login(request, user)
                                return redirect("std_dashboard")
                        else:
                            messages.error(request, "Verification failed. Try again.")
                            return redirect("std_login")

                except Student.DoesNotExist:
                    messages.error(request, "Student profile not found.")
                    return redirect("std_login")
            else:
                messages.error(request, "Invalid credentials.")
                return redirect("std_login")

        messages.error(request, "Something went wrong.")
        return redirect("std_login")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('std_login')



def verify_otp(request):
    try:
        """Verify the entered OTP"""
        email = request.session.get("otp_email")
        if not email:
            return redirect("std_login")

        if request.method == "POST":
            entered_otp = request.POST.get("otp")
            otp_entry = EduOTP.objects.filter(email=email, is_verified=False).first()

            if otp_entry and not otp_entry.is_expired():
                if otp_entry.otp == int(entered_otp):
                    otp_entry.is_verified = True
                    otp_entry.save()
                    user = User.objects.filter(email=email).first()
                    login(request, user)
                    return redirect("std_dashboard")
                else:
                    messages.error(request, "Incorrect OTP.")
            else:
                messages.error(request, "OTP expired. Please request a new one.")

        return render(request, "std_verification.html", {"email": email})
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('std_login')



def resend_otp(request):
    try:
        """Resend OTP if expired"""
        email = request.session.get("otp_email")
        if not email:
            return redirect("std_login")
        
        referer_url = request.session.get('referer_url', 'std_login')

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
            send_otp(email,otp_type="resend_otp")
            messages.success(request, "A new OTP has been sent to your email.")

        return redirect(referer_url)
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('std_login')



def std_forget_password(request):
    email_session = request.session.get("otp_email")
    if email_session:
        del request.session["otp_email"]

    if request.method == "POST":
        email = request.POST.get("email")
        
        try:
            user = User.objects.get(email=email, user_type='student')
            otp = send_otp(email,otp_type="reset_password")
            request.session["otp_email"] = email
            messages.success(request, "OTP sent to your email.")
            return redirect("std_reset_password")
        except User.DoesNotExist:
            messages.error(request, "No student account found with this email.")
    
    return render(request, "std_forget.html")



def std_reset_password(request):
    try:
        email = request.session.get("otp_email")
        if not email:
            return redirect("std_forget_password")

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
                        return redirect("std_login")
                    else:
                        messages.error(request, "Passwords do not match.")
                else:
                    messages.error(request, "Incorrect OTP.")
            else:
                messages.error(request, "OTP expired. Please request a new one.")

        return render(request, "std_reset.html", {"email": email})
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('std_dashboard')




def std_register(request):
    std_session = request.session.get("registration_data")
    if std_session:
        del request.session["registration_data"]

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            # Store data in session instead of saving immediately
            request.session['registration_data'] = {
                'username': form.cleaned_data['username'],
                'email': form.cleaned_data['email'],
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'password': form.cleaned_data['password1'],  
                'gender': form.cleaned_data['gender'],
            }
            email_add = form.cleaned_data['email']
            otp = send_otp(email_add,otp_type="register")
            request.session["otp_email"] = email_add
            return redirect('std_register_next')  
        else:
            # Add error messages for display
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error} ")
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'std_register1.html', {'form': form})



def std_register_next(request):
    registration_data = request.session.get('registration_data')
    if not registration_data:
        messages.error(request, "Please complete the first step of registration")
        return redirect('std_register')

    if request.method == 'POST':
        # Get form data
        phone = request.POST.get('phone')
        otp = request.POST.get('otp')
        address = request.POST.get('address')
        country = request.POST.get('country')
        state = request.POST.get('state')
        city = request.POST.get('city')
        zip_code = request.POST.get('zip_code')
        skills = request.POST.get('skills')
        bio = request.POST.get('bio')
        link = request.POST.get('link')
        level = request.POST.get('level')
        profile_pic = request.POST.get('selected-image-src')
        if profile_pic:
            image_path = os.path.join('img', 'img_auth', profile_pic)  # 'img/img_auth/circle.jpg' or similar
        else:
            image_path = os.path.join('img', 'img_auth', 'pentagon.jpg') 

        otp_entry = EduOTP.objects.filter(email=registration_data['email'], is_verified=False).first()
        if otp_entry and not otp_entry.is_expired():
            if otp_entry.otp == int(otp):
                otp_entry.is_verified = True
                otp_entry.save()
            else:
                messages.error(request, "Incorrect OTP.")
                return redirect('std_login')
        else:
            messages.error(request, "OTP expired. Please request a new one.")
            return redirect('std_login')

        try:
            # Create User object
            user = User.objects.create_user(
                username=registration_data['username'],
                email=registration_data['email'],
                password=registration_data['password'],
                first_name=registration_data['first_name'],
                last_name=registration_data['last_name'],
                user_type='student'
            )

            # Create Student object
            student = Student.objects.create(
                user=user,
                first_name=registration_data['first_name'],
                last_name=registration_data['last_name'],
                gender=registration_data['gender'],
                phone_number=phone,
                address=address,
                country=country,
                state=state,
                city=city,
                zip_code=zip_code,
                current_level=level,
                bio=bio,
                profile_picture=image_path if image_path else None
            )

            # Create StudentProfile
            StudentProfile.objects.create(
                student=student,
                skills=skills.split(',') if skills else [],
                bio=bio,
                interests=[],
                achievements=[]
            )


            subject_reg = 'Welcome to Our E-Learning Platform EduConnect'
            des_mess = 'Thank you for signing up on our platform. We are happy to have you! your account as been created..'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [registration_data['email']]  

            # send_mail(subject_reg, des_mess, from_email, recipient_list)

            # Clear session data
            del request.session['registration_data']

            messages.success(request, "Registration successful! Please login.")
            return redirect('std_login')
        

        except Exception as e:
            messages.error(request, f"Registration failed: {str(e)}")
            return render(request, 'std_register2.html')

    return render(request, 'std_register2.html')




def search_courses(request):
    query = request.GET.get('q', '')
    
    if not query:
        return redirect('home')
    
    # Track search query
    try:
        search_query, created = SearchQuery.objects.get_or_create(query=query.lower())
        if not created:
            search_query.count += 1
            search_query.save()
    except:
        # If SearchQuery model doesn't exist, just pass
        pass
    
    # Save search query to session for search history
    if request.user.is_authenticated:
        search_history = request.session.get('search_history', [])
        # Add current query if not already in history
        if query not in search_history:
            search_history.insert(0, query)  # Add to beginning
            # Keep only the last 10 searches
            search_history = search_history[:10]
            request.session['search_history'] = search_history
    
    # Split the query into words for more flexible searching
    query_words = query.split()
    
    # Create a Q object for each word in the query
    q_objects = Q()
    for word in query_words:
        q_objects |= Q(title__icontains=word) | Q(description__icontains=word)
    
    # Filter courses that match any of the words and are active
    courses = Course.objects.filter(q_objects, is_display=True).distinct()
    
    # Add additional filters if needed
    category = request.GET.get('category', '')
    if category:
        courses = courses.filter(category=category)
    
    # Sort options
    sort_by = request.GET.get('sort', 'relevance')
    if sort_by == 'price_low':
        courses = courses.order_by('price')
    elif sort_by == 'price_high':
        courses = courses.order_by('-price')
    elif sort_by == 'rating':
        courses = courses.order_by('-rating')
    elif sort_by == 'newest':
        courses = courses.order_by('-created_at')
    elif sort_by == 'popularity':
        courses = courses.order_by('-enroll')
    
    # Get "did you mean" suggestion if no results
    did_you_mean = None
    if not courses.exists() and len(query) > 3:
        # Get all course titles for fuzzy matching
        all_titles = Course.objects.filter(is_display=True).values_list('title', flat=True)
        
        # Try to find close matches
        matches = get_close_matches(query.lower(), [title.lower() for title in all_titles], n=1, cutoff=0.6)
        if matches:
            # Find the original case version
            for title in all_titles:
                if title.lower() == matches[0]:
                    did_you_mean = title
                    break
    
    # Pagination
    paginator = Paginator(courses, 12)  # Show 12 courses per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get all categories for filter sidebar
    categories = Course.objects.filter(is_display=True).values_list('category', flat=True).distinct()
    
    # Get trending searches
    try:
        trending_searches = SearchQuery.objects.order_by('-count')[:5]
    except:
        trending_searches = []
    
    context = {
        'query': query,
        'courses': page_obj,
        'total_results': courses.count(),
        'categories': categories,
        'selected_category': category,
        'sort_by': sort_by,
        'did_you_mean': did_you_mean,
        'trending_searches': trending_searches,
        'search_history': request.session.get('search_history', [])[:5] if request.user.is_authenticated else [],
    }
    
    return render(request, 'search_results.html', context)




def clear_search_history(request):
    if request.user.is_authenticated and 'search_history' in request.session:
        del request.session['search_history']

    return redirect(request.META.get('HTTP_REFERER', 'home'))


