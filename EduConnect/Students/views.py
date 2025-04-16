from django.shortcuts import get_object_or_404, render,redirect
from videoconference_app.models import Webinar,WebinarAttendance
from .models import Payment, Student, StudentFeedback, StudentNotificationDashboard,StudentNotificationSettings,UserCalendarEvent,StudentProfile
from Teachers.models import Teacher
from Course_Module.models import Course,Content,Certificate,Assignment,AssignmentSubmission,StudentProgress,CourseFeatures,CourseLearning,CourseSkills
from EduAssessment.models import Enrollment, Form, FormAccessControl, StudentResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import simpleSplit
from io import BytesIO
from django.http import HttpResponse, JsonResponse
from datetime import datetime, timedelta
from django.db.models import Q
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.utils import timezone
from django.db.models import Avg
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

@login_required
def std_home(request):
    context = {}
    if request.user.user_type != 'student':
        return JsonResponse({"error": "You must be a student to access this content."}, status=403)

    student = request.user.student
    student_notifications = StudentNotificationDashboard.objects.filter(student=student).order_by('-created_at')[:10]
    print(student_notifications)
    

    notifications = []
    for notification in student_notifications:
        notifications.append({
            'id': notification.id,
            'message': notification.message,
            'timestamp': notification.created_at.strftime('%Y-%m-%d %H:%M:%S') 
        })

    return JsonResponse({"student_notifications": notifications})


@login_required
def std_dashboard(request):
    if request.user.user_type != 'student': 
        messages.error(request, "You must be a student to access this page.")
        return redirect('std_login')
    
    try:
        student = Student.objects.get(user=request.user)
        student_notifications = StudentNotificationDashboard.objects.filter(student=student).order_by('-created_at')[:10]

        
        # Course Statistics
        total_courses = Enrollment.objects.filter(student=student).count()
        active_courses = Enrollment.objects.filter(student=student, status='Active').count()
        completed_courses = Certificate.objects.filter(student=student).count()
        
        # Test/Quiz Statistics
        total_tests = StudentResponse.objects.filter(student=student).count()
        avg_score = StudentResponse.objects.filter(student=student).aggregate(Avg('score'))['score__avg'] or 0
        
        # Webinar Statistics
        total_webinars = WebinarAttendance.objects.filter(student=student).count()
        attended_webinars = WebinarAttendance.objects.filter(student=student, attended=True).count()
        webinar_attendance_rate = (attended_webinars/total_webinars * 100) if total_webinars > 0 else 0
        
        # Course Progress Data
        course_progress = []
        enrollments = Enrollment.objects.filter(student=student).select_related('course')
        for enrollment in enrollments:
            total_content = Content.objects.filter(course=enrollment.course).count()
            completed_content = StudentProgress.objects.filter(
                student=student, 
                content__course=enrollment.course,
                is_completed=True
            ).count()
            progress = (completed_content/total_content * 100) if total_content > 0 else 0
            
            latest_progress = StudentProgress.objects.filter(
                student=student,
                content__course=enrollment.course
            ).first()
            
            course_progress.append({
                'course': enrollment.course.title,
                'progress': round(progress, 2),
                'last_active': latest_progress.content.title if latest_progress else "No activity"
            })
        
        # Weekly Activity Data (based on enrollment dates instead of updated_at)
        from datetime import datetime, timedelta
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        weekly_data = []
        week_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

        for i in range(7):
            day_date = week_start + timedelta(days=i)
            day_start = day_date.replace(hour=0, minute=0, second=0, microsecond=0)  # Start of the day
            day_end = day_start + timedelta(days=1)
            # Filter for the specific day's progress
            count = StudentProgress.objects.filter(
                student=student,
                is_completed=True,
                id__isnull=False,
                created_at__gte=day_start,  # Progress that started after the beginning of the day
                created_at__lt=day_end
            ).count()
            weekly_data.append(count)

        weekly_activity = {
            'labels': json.dumps(week_days),
            'data': json.dumps(weekly_data)
        }
        
        # Course Categories Data (based on actual enrolled courses)
        categories = {}
        for enrollment in Enrollment.objects.filter(student=student).select_related('course'):
            category = enrollment.course.category
            total_content = Content.objects.filter(course=enrollment.course).count()
            completed_content = StudentProgress.objects.filter(
                student=student,
                content__course=enrollment.course,
                is_completed=True
            ).count()
            
            progress = (completed_content/total_content * 100) if total_content > 0 else 0
            
            if category in categories:
                categories[category] = max(categories[category], progress)
            else:
                categories[category] = progress

        course_categories = {
            'labels': json.dumps(list(categories.keys())),
            'data': json.dumps([round(progress, 2) for progress in categories.values()])
        }
        
        context = {
            'student': student,
            'stats': {
                'total_courses': total_courses,
                'active_courses': active_courses,
                'completed_courses': completed_courses,
                'completion_rate': round((completed_courses/total_courses * 100) if total_courses > 0 else 0, 2),
                'total_tests': total_tests,
                'avg_score': round(avg_score, 2),
                'total_webinars': total_webinars,
                'attended_webinars': attended_webinars,
                'webinar_attendance_rate': round(webinar_attendance_rate, 2)
            },
            'course_progress': course_progress,
            'chart_data': {
                'weekly_activity': weekly_activity,
                'course_categories': course_categories
            },
            'student_notifications': student_notifications,
        }
        
        return render(request, 'std_dashboard.html', context)
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('std_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('std_login')


@login_required
def std_profile(request):
    if request.user.user_type != 'student': 
        messages.error(request, "You must be a student to access this page.")
        return redirect('std_login')
    try:
        student = Student.objects.get(user=request.user)
        notification, created = StudentNotificationSettings.objects.get_or_create(student=student)
        student_notifications = StudentNotificationDashboard.objects.filter(student=student).order_by('-created_at')[:10]

        notify=''
        if notification.email_notifications:
            notify = 'on'
        else:
            notify = 'off'

        return render(request, 'std_profile.html', {'student': student,'notify':notify,'student_notifications':student_notifications})
    
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('std_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('std_dashboard')



@login_required
def std_profile_edit(request):
    if request.user.user_type != 'student': 
        messages.error(request, "You must be a student to access this page.")
        return redirect('std_login')
    
    try:
        student = Student.objects.get(user=request.user)
        notification, created = StudentNotificationSettings.objects.get_or_create(student=student)
        student_notifications = StudentNotificationDashboard.objects.filter(student=student).order_by('-created_at')[:10]

        if request.method == "POST":
            student.first_name = request.POST.get("first_name")
            student.last_name = request.POST.get("last_name")
            student.date_of_birth = request.POST.get("date_of_birth")
            student.gender = request.POST.get("gender")
            student.phone_number = request.POST.get("phone_number")
            student.address = request.POST.get("address")
            student.state = request.POST.get("state")
            student.city = request.POST.get("city")
            student.country = request.POST.get("country")
            student.program = request.POST.get("program")
            student.current_level = request.POST.get("current_level")
            student.bio = request.POST.get("bio")
            student.social_links = request.POST.get("social_links")

            # Update notification settings
            notification.email_notifications = request.POST.get("notifications_enabled") == "on"
            notification.save()

            student.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('std_profile')  

        notify = 'checked' if notification.email_notifications else 'unchecked'

        return render(request, 'std_profile2.html', {'student': student, 'notify': notify,'student_notifications':student_notifications})
    
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('std_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('std_dashboard')



@login_required
def std_courses(request):
    # Ensure only students can access
    if request.user.user_type != 'student':  
        messages.error(request, "You must be a student to access this page.")
        return redirect('std_login')

    try:
        student = Student.objects.get(user=request.user)  # Fetch logged-in student
        student_notifications = StudentNotificationDashboard.objects.filter(student=student).order_by('-created_at')[:10]
        enrollments = Enrollment.objects.filter(student=student)

        total_assignments = 0
        pending_assignments = 0
        completed_assignments = 0
        rework_assignments = 0
        courses_progress = []

        for enrollment in enrollments:
            course = enrollment.course
            content_list = Content.objects.filter(course=course)

            # Get assignments for this course
            course_assignments = Assignment.objects.filter(question__in=content_list)
            total_assignments += course_assignments.count()

            # Get submitted assignments
            submitted = AssignmentSubmission.objects.filter(
                student=student,
                assignment__in=course_assignments
            )
            completed_assignments += submitted.filter(status='completed').count()
            pending_assignments += submitted.filter(status='pending').count()
            rework_assignments += submitted.filter(status='rework').count()

            # Calculate course progress
            total_contents = content_list.count()
            completed_contents = StudentProgress.objects.filter(
                student=student,
                content__in=content_list,
                is_completed=True
            ).count()

            # Calculate progress percentage
            total_pages = len(content_list)  # 1 point per page
            total_points = total_pages + (total_assignments * 2)  # Each assignment = 2 points
            completed_points = completed_contents + (submitted.count() * 2)

            # Calculate progress percentage
            progress_percentage = (completed_points / total_points * 100) if total_points > 0 else 0
            progress_percentage = min(100, round(progress_percentage, 2))
            # print(f"Course: {course.title}, Progress: {progress_percentage}%")

            # Get current chapter
            current_chapter = content_list.filter(
                studentprogress__student=student,
                studentprogress__is_completed=False
            ).order_by('order').first()

            if not current_chapter:
                current_chapter = content_list.order_by('order').first()

            courses_progress.append({
                'course': course,
                'current_chapter': current_chapter,
                'progress': round(progress_percentage, 2),
                'completed_chapters': completed_contents,
                'total_chapters': total_contents,
                'remaining_time': enrollment.remaining_time_in_days(),
            })

        context = {
            'pending_assignments': pending_assignments,
            'completed_assignments': completed_assignments,
            'rework_assignments': rework_assignments,
            'total_assignments': total_assignments,
            'courses_progress': courses_progress,
            'student': student,
            'student_notifications':student_notifications,
        }

        return render(request, 'std_courses.html', context)

    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('std_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('std_dashboard')



@login_required
def std_achievement(request):
    if request.user.user_type != 'student': 
        messages.error(request, "You must be a student to access this page.")
        return redirect('std_login')
    
    try:
        student = Student.objects.get(user=request.user)
        student_notifications = StudentNotificationDashboard.objects.filter(student=student).order_by('-created_at')[:10]
        # Fetch enrolled courses with completion data
        enrollments = Enrollment.objects.filter(student=student).select_related('course')
        course_data = []
        
        for enrollment in enrollments:
            total_content = Content.objects.filter(course=enrollment.course).count()
            completed_content = StudentProgress.objects.filter(
                student=student, 
                content__course=enrollment.course, 
                is_completed=True
            ).count()
            
            completion_percentage = (completed_content / total_content * 100) if total_content > 0 else 0
            
            course_data.append({
                'title': enrollment.course.title,
                'completion_date': enrollment.course_end_date(),
                'enrollment_date': enrollment.enrollment_date,
                'percentage': round(completion_percentage, 2),
                'duration': f"{enrollment.course.months} months",
                'status': enrollment.status,
                'teacher': enrollment.course.teacher.first_name + ' ' + enrollment.course.teacher.last_name
            })

        # Fetch webinars
        webinars = Webinar.objects.filter(
            course__enrolled_students__student=student
        ).order_by('-scheduled_date')

        webinar_data = []
        for webinar in webinars:
            attendance = WebinarAttendance.objects.filter(
                student=student,
                webinar=webinar
            ).first()
            
            webinar_data.append({
                'title': webinar.title,
                'date': webinar.scheduled_date,
                'course': webinar.course.title,
                'teacher': webinar.teacher.user.get_full_name(),
                'status': webinar.status,
                'attended': 'Present' if attendance and attendance.attended else 'Not Attended',
                'duration': f"{(attendance.leave_time - attendance.join_time).total_seconds() // 60} mins" if attendance and attendance.attended else '-'
            })

        # Fetch form submissions and scores
        form_submissions = StudentResponse.objects.filter(
            student=student
        ).select_related('form').order_by('-submitted_at')
        
        submission_data = []
        for submission in form_submissions:
            submission_data.append({
                'title': submission.form.title,
                'type': 'Test/Quiz',
                'date': submission.submitted_at,
                'score': submission.score,
                'course': submission.form.course.title
            })

        # Fetch certificates
        certificates = Certificate.objects.filter(
            student=student
        ).select_related('course').order_by('-created_at')
        
        certificate_data = []
        for cert in certificates:

            certificate_data.append({
                'title': cert.course.title,
                'organization': 'EduConnect',  
                'issue_date': cert.created_at,
                'certificate_id': f'CERT{cert.id}',
                'teacher': cert.course.teacher.first_name + ' ' + cert.course.teacher.last_name,
                'course': cert.course,
                'verify_link': cert.course.id,
                'download_link': f'/course/{cert.course.id}/certificate/'
            })

        context = {
            'student': student,
            'course_data': course_data,
            'submission_data': submission_data,
            'webinar_data': webinar_data,
            'certificates': certificate_data,
            'student_notifications':student_notifications,
        }
        
        return render(request, 'std_achievement.html', context)
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('std_login')

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('std_dashboard')



@login_required
def std_events(request):
    if request.user.user_type != 'student': 
        messages.error(request, "You must be a student to access this page.")
        return redirect('std_login')
    try:

        student = Student.objects.get(user=request.user)
        student_notifications = StudentNotificationDashboard.objects.filter(student=student).order_by('-created_at')[:10]
        events = []
        current_date = timezone.now()
        
        # Get all the courses the student is enrolled in
        enrolled_courses = Enrollment.objects.filter(student=student).values_list('course', flat=True)
        all_forms = Form.objects.filter(course__in=enrolled_courses)

        past_forms_data = []
        for form in all_forms:
            has_access = FormAccessControl.objects.filter(
                student=student, 
                form=form, 
                has_access=True
            ).exists()
            
            response = StudentResponse.objects.filter(
                student=student, 
                form=form
            ).first()

            # Check if form is submitted first
            if response:
                past_forms_data.append({
                    'id': form.id,
                    'title': form.title,
                    'date': response.submitted_at.strftime('%d.%m.%Y'),
                    'course': form.course.title,
                    'has_access': True,
                    'status': 'Submitted',
                    'score': response.score,
                    'color': '#28a745'
                })
            # Then check if it's upcoming
            elif form.event_date > current_date:
                past_forms_data.append({
                    'id': form.id,
                    'title': form.title,
                    'date': form.event_date.strftime('%d.%m.%Y'),
                    'course': form.course.title,
                    'has_access': has_access,
                    'status': 'Upcoming',
                    'color': '#4d70f1'
                })
            # Then check for past forms with access but not submitted
            elif has_access and form.event_date <= current_date:
                past_forms_data.append({
                    'id': form.id,
                    'title': form.title,
                    'date': form.event_date.strftime('%d.%m.%Y'),
                    'course': form.course.title,
                    'has_access': True,
                    'status': 'Not Submitted',
                    'color': '#ffc107'
                })
            # Finally, forms without access
            else:
                past_forms_data.append({
                    'id': form.id,
                    'title': form.title,
                    'date': form.event_date.strftime('%d.%m.%Y'),
                    'course': form.course.title,
                    'has_access': False,
                    'status': 'No Access',
                    'color': '#dc3545'
                })

        # Sort forms by date
        past_forms_data.sort(key=lambda x: datetime.strptime(x['date'], '%d.%m.%Y'), reverse=True)

        # Fetch webinars related to the student
        upcoming_webinars = Webinar.objects.filter(
            course__enrolled_students__student=student,
            
        ).order_by('-status', 'scheduled_date')

        user_events = UserCalendarEvent.objects.filter(student=student)
        for event in user_events:
            events.append({
                'date': event.event_date.strftime('%Y-%m-%d'),
                'title': event.title,
                'description': event.description,
                'type': 'user_event',
                'color': '##90EE90'
            })
        
        # Webinar dates
        webinars = Webinar.objects.filter(course__enrolled_students__student=student)
        for webinar in webinars:
            events.append({
                'date': webinar.scheduled_date.strftime('%Y-%m-%d'),
                'title': f"Webinar: {webinar.title}",
                'type': 'webinar',
                'color': '#FFCCCB'
            })

        # Form/Test dates
        forms = Form.objects.filter(
            Q(course__enrolled_students__student=student) & 
            Q(formaccesscontrol__has_access=True)
        )
        for form in forms:
            events.append({
                'date': form.event_date.strftime('%Y-%m-%d'),
                'title': f"Test: {form.title}",
                'type': 'test',
                'color': '#FFB6C1'
            })

        # Course enrollment and end dates
        enrollments = Enrollment.objects.filter(student=student)
        for enrollment in enrollments:
            events.append({
                'date': enrollment.enrollment_date.strftime('%Y-%m-%d'),
                'title': f"Enrolled: {enrollment.course.title}",
                'type': 'enrollment',
                'color': '#ADD8E6'
            })
            events.append({
                'date': enrollment.course_end_date().strftime('%Y-%m-%d'),
                'title': f"Course Ends: {enrollment.course.title}",
                'type': 'course_end',
                'color': '#d3f14d'
            })

        # Assignment submissions
        submissions = AssignmentSubmission.objects.filter(student=student)
        for submission in submissions:
            events.append({
                'date': submission.submitted_at.strftime('%Y-%m-%d'),
                'title': f"Submitted: {submission.assignment.title}",
                'type': 'submission',
                'color': '#818a03'
            })

        
        events_json = json.dumps(events, cls=DjangoJSONEncoder)

        # Render the events page
        return render(request, 'std_events.html', {
            'events': events_json,
            'student': student,
            'past_forms': past_forms_data,
            'upcoming_webinars': upcoming_webinars,
            'student_notifications':student_notifications,
        })

    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('std_login')

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('std_dashboard')



@login_required
def calendar_event_create(request):
    if request.user.user_type != 'student': 
        messages.error(request, "You must be a student to access this page.")
        return redirect('std_login')
    if request.method == 'POST':
        data = json.loads(request.body)
        student = Student.objects.get(user=request.user)
        
        event = UserCalendarEvent.objects.create(
            student=student,
            title=data['title'],
            description=data['description'],
            event_date=data['date'],
        )
        
        return JsonResponse({'status': 'success', 'event': {
            'id': event.id,
            'title': event.title,
            'date': event.event_date,
            'description': event.description,
            'type': 'user_event',
            'color': '#461e00'  # You can customize this color
        }})



@login_required
def std_pay(request):
    if request.user.user_type != 'student': 
        messages.error(request, "You must be a student to access this page.")
        return redirect('std_login')
    try:
        user = request.user 
        student = Student.objects.get(user=user)  
        payments = Payment.objects.filter(student=student)  
        total_paid = sum(payment.amount for payment in payments if payment.payment_status == "success")
        student_notifications = StudentNotificationDashboard.objects.filter(student=student).order_by('-created_at')[:10]
        
        return render(request, 'std_payments.html', {
            'payments': payments,
            'total_paid': total_paid,
            'student': student,
            'student_notifications':student_notifications,
        })
    
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('std_login')
    
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('std_dashboard') 



@login_required
def std_payment(request, pay_id):
    if request.user.user_type != 'student': 
        messages.error(request, "You must be a student to access this page.")
        return redirect('std_login')
    
    context = {}

    try:
        student = Student.objects.get(user=request.user) 
        payment = get_object_or_404(Payment, id=pay_id) 
        student_check = payment.student  
        student_notifications = StudentNotificationDashboard.objects.filter(student=student).order_by('-created_at')[:10]

        if student_check != student:  
            return redirect('std_dashboard') 

        course_id = payment.course.id  
        course = get_object_or_404(Course, id=course_id) 
        
        features = CourseFeatures.objects.filter(course=course)  
        learning = CourseLearning.objects.filter(course=course) 
        skills = CourseSkills.objects.filter(course=course)  
        
        certificate = Certificate.objects.filter(student=student, course=course).exists()
        
        if certificate:
            certificate_status = 'Available'
        else:
            certificate_status = 'Not Yet'
        
        context = {
            "payment": payment,
            "course": course,
            "student": student,
            "certificate_status": certificate_status,
            'features': features,
            'learning': learning,
            'skills': skills,
            'student_notifications':student_notifications,
        }
        
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('std_login')    
    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        return redirect('std_login') 
    
    return render(request, 'std_payments2.html', context)



@login_required
def generate_invoice_pdf(request, pay_id):
    if request.user.user_type != 'student': 
        messages.error(request, "You must be a student to access this page.")
        return redirect('std_login')

    try:
        student = Student.objects.get(user=request.user)  
        
        payment = get_object_or_404(Payment, id=pay_id) 
        student_check = payment.student  
        
        course = payment.course  
        if student_check != student:  
            return redirect('std_dashboard')  

        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(200, height - 50, "EduConnect Payment Invoice")

        pdf.setFont("Helvetica", 12)
        pdf.drawString(50, height - 100, f"Invoice ID: {payment.payment_id}")
        pdf.drawString(50, height - 130, f"Student Name: {student.user.get_full_name()}")
        pdf.drawString(50, height - 160, f"Course: {course.title}")
        pdf.drawString(50, height - 190, f"Amount Paid: ₹{payment.amount}")
        pdf.drawString(50, height - 220, f"Payment Status: {payment.payment_status}")
        pdf.drawString(50, height - 250, f"Payment Method: {payment.payment_method if payment.payment_method else 'N/A'}")
        pdf.drawString(50, height - 280, f"Payment Date: {payment.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, height - 330, "Thank you for your payment!")

        pdf.showPage()
        pdf.save()

        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=Invoice_{payment.payment_id}.pdf'
        return response

    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('std_dashboard')  
    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        return redirect('std_dashboard')



@login_required
def std_feedback(request):
    context = {}
    if request.user.user_type != 'student':
        messages.error(request, "You must be a student to access this page.")
        return redirect('std_login')
    
    try:
        student = Student.objects.get(user=request.user)
        student_notifications = StudentNotificationDashboard.objects.filter(student=student).order_by('-created_at')[:10]

        if request.method == "POST":
            category = request.POST.get("feedbackTitle")
            custom_category = request.POST.get("customTitle", "") if category == "other" else ""
            feedback_text = request.POST.get("feedbackInput")
            rating = request.POST.get('rating') if request.POST.get('rating') else 1
            suggestions = request.POST.get("suggestions", "")
            file = request.FILES.get("upload")
            
            if not category or not feedback_text or not rating:
                context['message'] = 'All fields are required.'
                return render(request, 'std_feedback.html', context)
            
            if category == 'other':
                category = 'Other'

            feedback = StudentFeedback.objects.create(
                student=student,  
                category=category,
                custom_category=custom_category,
                feedback_text=feedback_text,
                rating=rating,
                suggestions=suggestions,
                file=file,
            )
            
            
            messages.success(request, "Feedback submitted successfully!")
            return redirect(request.path)
        context['student'] = student
        context['student_notifications'] = student_notifications
        return render(request, 'std_feedback.html', context)

    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('std_login')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('std_dashboard')



@login_required
def std_setting(request):
    if request.user.user_type != 'student':
        messages.error(request, "You must be a student to access this page.")
        return redirect('std_login')

    context = {}
    try:
        student = request.user.student
        settings, created = StudentNotificationSettings.objects.get_or_create(student=student)
        student_notifications = StudentNotificationDashboard.objects.filter(student=student).order_by('-created_at')[:10]

        if request.method == "POST":
            settings.email_notifications = 'email_notifications' in request.POST
            settings.auth_notifications = 'auth_notifications' in request.POST
            # settings.course_notifications = 'course_notifications' in request.POST
            settings.save()
            messages.success(request, "Notification settings updated successfully!")
        context['student'] = student
        context['settings'] = settings
        context['student_notifications'] = student_notifications
        return render(request, 'std_system.html', context)

    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('std_login')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('std_dashboard')



@login_required
def download_payment_pdf(request):
    if request.user.user_type != 'student':
        messages.error(request, "You must be a student to access this page.")
        return redirect('std_login')
    try:
        student = request.user.student
        payments = Payment.objects.filter(student=student)

        # Create a HttpResponse object with PDF content type
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="payment_details_{student.user.first_name}.pdf"'

        # Create a PDF object
        pdf = canvas.Canvas(response, pagesize=letter)

        # Add some text to the PDF
        pdf.drawString(100, 750, f"Payment Details for {student.user.first_name} {student.user.last_name}")
        pdf.drawString(100, 730, f"Student ID: {student.student_id}")
        pdf.drawString(100, 710, f"Email: {student.user.email}")
        pdf.drawString(100, 690, "------------------------------------")
        y_position = 670

        for payment in payments:
            pdf.drawString(100, y_position, f"Payment ID: {payment.payment_id}")
            y_position -= 20  
            pdf.drawString(100, y_position, f"Course: {payment.course.title}")
            y_position -= 20
            pdf.drawString(100, y_position, f"Amount: {payment.amount} Rupees")
            y_position -= 20
            pdf.drawString(100, y_position, f"Payment Status: {payment.get_payment_status_display()}")
            y_position -= 30  
            pdf.drawString(100, y_position, f"-----------------")
            y_position -= 30 

        pdf.showPage()
        pdf.save()

        return response
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('std_login')

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('std_dashboard')



@login_required
def deactivate_account(request):
    if request.user.user_type != 'student':
        messages.error(request, "You must be a student to access this page.")
        return redirect('std_login')
    try:
        user = request.user.student
        user.is_active = False
        user.save()
        return redirect('std_login')
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('std_login')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('std_dashboard')
    
