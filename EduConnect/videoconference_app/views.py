from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from Teachers.models import Teacher
from Students.models import Student
from Course_Module.models import Course
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from .models import Webinar, WebinarAttendance
from EduAssessment.models import Enrollment
from django.contrib import messages
from django.utils import timezone
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import logging

@login_required
def teacher_join_meeting(request, meeting_id, course_id,webinar_id):
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')
    # teacher_email = request.user.email
    try:
        teacher = Teacher.objects.get(user=request.user)
        teacher = get_object_or_404(Teacher, teacher_id=teacher.teacher_id)
        course = get_object_or_404(Course, id=course_id)
        
        if course.teacher != teacher:
            return HttpResponseForbidden("Invalid Action: You are not the course creator.")

        if course.meeting_code != meeting_id:
            return HttpResponseBadRequest("Invalid Meeting ID.")

        webinar = get_object_or_404(Webinar, id=webinar_id, course=course)

        if not webinar.status:
            return HttpResponseBadRequest("This webinar is not active.")

        return render(request, 'meeting_videocall.html', {'name': teacher.first_name + " " + teacher.last_name, 'roomID': meeting_id})
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')


@login_required
def student_join_meeting(request, meeting_id, course_id,webinar_id):
    if request.user.user_type != 'student': 
        messages.error(request, "You must be a student to access this page.")
        return redirect('std_login')

    try:
        student = Student.objects.get(user=request.user)  
        student = get_object_or_404(Student, student_id=student.student_id)
        course = get_object_or_404(Course, id=course_id)

        if course.meeting_code != meeting_id:
            return HttpResponseBadRequest("Invalid Meeting ID.")

        enrollment = Enrollment.objects.filter(student=student, course=course).first()
        
        if not enrollment:
            return HttpResponseForbidden("Invalid Action: You are not enrolled in this course.")

        # webinar = get_object_or_404(Webinar, course=course)
        webinar = get_object_or_404(Webinar, id=webinar_id, course=course)

        if not webinar.status:
            return HttpResponseBadRequest("This webinar is not active.")
        
        # WebinarAttendance.objects.get_or_create(
        #     student=student,
        #     webinar=webinar,
        #     defaults={
        #         'attended': True,
        #         'join_time': timezone.now()  # Set the join_time when the student joins
        #     }
        # )

        return render(request, 'meeting_videocall.html', {'name': student.first_name + " " + student.last_name, 'roomID': meeting_id,'webinar':webinar})
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('std_login') 
    except Course.DoesNotExist:
        messages.error(request, "Course not found.")
        return redirect('std_dashboard')
    except Webinar.DoesNotExist:
        messages.error(request, "Webinar not found.")
        return redirect('std_dashboard')  
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('std_dashboard')
    


@csrf_exempt
@require_http_methods(["POST"])
def record_attendance(request):
    print("Attendance recording endpoint hit")
    try:
        data = json.loads(request.body)
        webinar_id = data.get('webinar_id')
        action = data.get('action')
        timestamp = data.get('timestamp')
        
        webinar = get_object_or_404(Webinar, id=webinar_id)
        student = get_object_or_404(Student, user=request.user)
        
        # For join action, create or get attendance record with both times set
        if action == 'join':
            attendance, created = WebinarAttendance.objects.get_or_create(
                student=student,
                webinar=webinar,
                defaults={
                    'attended': True,
                    'join_time': timestamp,
                    'leave_time': timestamp  # Set initial leave time same as join time
                }
            )
            if not created:
                attendance.join_time = timestamp
                attendance.leave_time = timestamp
                attendance.save()
                
        # For leave action, only update the leave time
        elif action == 'leave':
            attendance = WebinarAttendance.objects.filter(
                student=student,
                webinar=webinar
            ).first()
            
            if attendance:
                attendance.leave_time = timestamp
                attendance.save()
        
        return JsonResponse({'status': 'success', 'action': action})
        
    except Exception as e:
        print(f"Error in record_attendance: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)