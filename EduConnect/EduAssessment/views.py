from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.urls import reverse
from Course_Module.models import Course
from .models import Enrollment, Form,Question,StudentResponse,FormAccessControl
from Students.models import Student, TeacherNotificationDashBoard,StudentNotificationDashboard
from Teachers.models import Teacher
from django.db.models import Sum, Count, Max
from django.utils.timezone import now
from django.http import JsonResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Form, Question
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Form, Question
import ast
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.utils import timezone



def test_index(request):
    context={}
    return render(request, "test_index.html", context)

@login_required
def test_home(request):
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')
    try:
        context={}
        teacher = Teacher.objects.get(user=request.user)
        form = Form.objects.filter(course__teacher=teacher)
        courses = Course.objects.filter(teacher=teacher)  # Fetch courses created by the teacher
        context['courses'] = courses
        context['form'] = form
        return render(request, "test_home.html", context)
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')
    

@login_required
def create_form(request):
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')
    try:
        if request.method == "POST":
            title = request.POST.get("title")
            course_id = request.POST.get("course_id")
            form_due_date = request.POST.get("formdate")

            if not title or not course_id or not form_due_date:
                messages.error(request, "Please provide all required fields.")
                return redirect("test_home")  

            course = get_object_or_404(Course, id=course_id)
            form = Form.objects.create(course=course, title=title,event_date=form_due_date)
            return redirect("test_form", form_id=form.id)

        return redirect("test_home")
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')
    

@login_required
def test_form(request,form_id):
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')
    try:
        context={}
        form = get_object_or_404(Form, id=form_id)
        course_check = form.course  
        if course_check.teacher != request.user.teacher:  
            messages.error(request, "You do not have permission to access this form.")
            return redirect('test_home')
        context['form'] = form
        context['form_id'] = form_id
        return render(request, "test_form.html", context)
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')


@login_required
def save_questions(request,form_id):
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')
    try:
        form = get_object_or_404(Form, id=form_id)
        course_check = form.course  
        if course_check.teacher != request.user.teacher:  
            messages.error(request, "You do not have permission to access this form.")
            return redirect('test_home')

        if request.method == "POST":
            
            # Extract question data from POST request
            question_texts = request.POST.getlist("question_text[]")
            question_types = request.POST.getlist("question_type[]")
            marks_list = request.POST.getlist("marks[]")
            options_list = request.POST.getlist("options[]")
            answer_keys = request.POST.getlist("answer_key[]")

            if not question_texts:
                return JsonResponse({"success": False, "error": "No questions provided"}, status=400)

            new_questions = []  # Temporary storage for new questions
            try:
                # Create new question objects but don't save yet
                for i in range(len(question_texts)):
                    new_question = Question(
                        form=form,
                        question_text=question_texts[i],
                        question_type=question_types[i],
                        marks=int(marks_list[i]) if marks_list[i].isdigit() else 0,
                        options=options_list[i],
                        answer_key=answer_keys[i]
                    )
                    new_questions.append(new_question)

                # If everything is valid, delete old questions
                Question.objects.filter(form=form).delete()

                # Save new questions to the database
                Question.objects.bulk_create(new_questions)

                return JsonResponse({"success": True, "message": "Questions saved successfully!"})

            except Exception as e:
                return JsonResponse({"success": False, "error": f"Failed to save questions: {str(e)}"}, status=500)

        return JsonResponse({"success": False, "error": "Invalid request"}, status=400)
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')



@login_required
def view_professor_form(request, form_id):
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')
    context={}
    try:
        form = get_object_or_404(Form, id=form_id)
        questions = Question.objects.filter(form=form)
        course_check = form.course  
        if course_check.teacher != request.user.teacher:  
            messages.error(request, "You do not have permission to access this form.")
            return redirect('test_home')
        

        # Ensure options and answer_key are lists
        for question in questions:
            question.options = eval(question.options) if isinstance(question.options, str) else question.options
            question.answer_key = eval(question.answer_key) if isinstance(question.answer_key, str) else question.answer_key

        total_questions = questions.count()
        total_marks = sum(question.marks for question in questions)

        context['form'] = form
        context['questions'] = questions
        context['total_questions'] = total_questions
        context['total_marks'] = total_marks
        context['form_id'] = form_id
        return render(request, "test_view.html", context)
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')


@login_required
def view_student_responses(request, form_id):
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')
    try:
        form = get_object_or_404(Form, id=form_id)
        course_check = form.course  
        if course_check.teacher != request.user.teacher:  
            messages.error(request, "You do not have permission to access this form.")
            return redirect('test_home')
        latest_responses = (
            StudentResponse.objects.filter(form=form).values('student_id').annotate(latest_submission=Max('submitted_at'), ))

        student_data = {}

        for entry in latest_responses:
            latest_response = StudentResponse.objects.filter(
                student_id=entry['student_id'], submitted_at=entry['latest_submission']
            ).select_related('student').first()

            if latest_response:
                student = latest_response.student

                student_aggregate = (
                    StudentResponse.objects
                    .filter(student=student, form=form)
                    .aggregate(
                        total_score=Sum('score'),
                        total_questions=Count('id'),
                        total_time=Sum('time_taken')
                    )
                )

                student_data[student.student_id] = {
                    "name": student.first_name,
                    "email": student.user.email,
                    "total_score": student_aggregate["total_score"] or 0,
                    "total_questions": student_aggregate["total_questions"] or 0,
                    "time_taken": student_aggregate["total_time"] or 0,
                    "submitted_at": latest_response.submitted_at,
                }

        return render(
            request,
            "test_response.html",
            {"form": form, "student_data": student_data,"form_id":form_id}
        )
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')


@login_required
def form_settings_view(request, form_id):
    if request.user.user_type != 'teacher': 
        messages.error(request, "You must be a instructor to access this page.")
        return redirect('tech_login')
    try:
        form = get_object_or_404(Form, id=form_id)
        formt = form.title
        course_check = form.course  
        if course_check.teacher != request.user.teacher:  
            messages.error(request, "You do not have permission to access this form.")
            return redirect('test_home')
        # Get all students who are enrolled in this form's course
        enrolled_students = Student.objects.filter(
            student_id__in=Enrollment.objects.filter(course=form.course).values_list("student_id", flat=True)
        )

        # Ensure each student has a FormAccessControl entry
        for student in enrolled_students:
            FormAccessControl.objects.get_or_create(student=student, form=form)

        # Fetch all students with access data
        student_access_list = FormAccessControl.objects.filter(form=form).select_related('student')

        if request.method == "POST":
            form.title = request.POST.get("form_name", form.title)  
            form.is_active = request.POST.get("is_active") == "on"
            form.save()

            # Update student access permissions
            for student_access in student_access_list:
                key = f"student_{student_access.student.student_id}"
                prev_access = student_access.has_access
                student_access.has_access = key in request.POST  # This will check if the checkbox was submitted
                student_access.save()
                
                if prev_access != student_access.has_access:
                    if student_access.has_access:
                        message = f"Your teacher has granted you access to the form '{form.title}'."
                    else:
                        message = f"Your teacher has revoked your access to the form '{form.title}'."
                    
                    # Create the notification for the student
                    StudentNotificationDashboard.objects.create(
                        student=student_access.student,
                        message=message,
                        created_at=now(),
                        is_read=False  # Notification is unread by default
                    )


            return JsonResponse({"message": "Settings updated successfully"})

        return render(request,"test_setting.html",{"form": form, "student_access_list": student_access_list,"formt":formt,"form_id":form_id})
    except Teacher.DoesNotExist:
        messages.error(request, "Instructor profile not found.")
        return redirect('tech_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('tech_overview')


@login_required
def student_take_test(request, form_id):
    if request.user.user_type != 'student': 
        messages.error(request, "You must be a student to access this page.")
        return redirect('std_login')
    
    try:
        form = get_object_or_404(Form, id=form_id)

        student = Student.objects.get(user=request.user) 

        current_time = timezone.now()
        event_date = form.event_date 
        if event_date:
            if current_time >= event_date:
                messages.error(request, "You cannot submit the test after the scheduled event date.")
                return redirect('std_dashboard')
            

        # Check if student is enrolled in the course
        is_enrolled = Enrollment.objects.filter(student=student, course=form.course, status="Active").exists()

        # Check if student has access to this test
        has_access = FormAccessControl.objects.filter(student=student, form=form, has_access=True).exists()

        # Check if the student has already submitted the test
        has_attempted = StudentResponse.objects.filter(student=student, form=form).exists()

        if not is_enrolled:
            messages.error(request, "You are not enrolled in this course.")
            return redirect('/')

        if not has_access:
            messages.error(request, "You do not have access to this test.")
            return redirect('/')

        if has_attempted:
            messages.error(request, "You have already submitted this test. You cannot take it again.")
            return redirect('std_events')  # Redirect to home or a specific page /Edu_Assessment/home/

        # Fetch and process questions
        questions = Question.objects.filter(form=form)
        for question in questions:
            if isinstance(question.options, str):  # If stored as a string
                try:
                    question.options = ast.literal_eval(question.options)  # Convert string to list safely
                except (SyntaxError, ValueError):
                    question.options = []  # Default to an empty list if conversion fails

        return render(request, 'test_std_view.html', {'form': form, 'questions': questions})
    except Student.DoesNotExist:
        messages.error(request, "Student not found.")
        return redirect('std_login')
    except Form.DoesNotExist:
        messages.error(request, "Test form not found.")
        return redirect('std_events')
    except Enrollment.DoesNotExist:
        messages.error(request, "You are not enrolled in this course.")
        return redirect('/')
    except FormAccessControl.DoesNotExist:
        messages.error(request, "No access to this test.")
        return redirect('/')
    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        return redirect('std_events')


@login_required
def submit_student_test(request, form_id):
    if request.user.user_type != 'student': 
        messages.error(request, "You must be a student to access this page.")
        return redirect('std_login')
    
    try:
        form = get_object_or_404(Form, id=form_id)
        student = Student.objects.get(user=request.user)
    
        time_taken = int(request.POST.get('time_taken', 0))
        # Check if student has access
        has_access = FormAccessControl.objects.filter(student=student, form=form, has_access=True).exists()
        if not has_access:
            messages.error(request, "You do not have access to submit this test.")
            return redirect('std_events')

        questions = Question.objects.filter(form=form)
        total_score = 0

        for question in questions:
            # Ensure options and answer_key are stored as lists
            if isinstance(question.options, str):
                try:
                    question.options = ast.literal_eval(question.options)  # Convert to list safely
                except (SyntaxError, ValueError):
                    question.options = []

            if isinstance(question.answer_key, str):
                try:
                    question.answer_key = ast.literal_eval(question.answer_key)  # Convert to list safely
                except (SyntaxError, ValueError):
                    question.answer_key = []

            selected_answer = request.POST.getlist(f'question_{question.id}')  

            # Ensure proper comparison (sorted for unordered MCQs)
            is_correct = sorted(selected_answer) == sorted(question.answer_key)  
            score = question.marks if is_correct else 0
            total_score += score

            

            StudentResponse.objects.create(
                student=student,
                form=form,
                question=question,
                selected_answer=selected_answer,  # Stores list as a string in DB
                time_taken=time_taken,  # Can be tracked using JavaScript timer
                score=score,
                submitted_at=now()
            )
            teacher = form.course.teacher  # Get the teacher associated with the form/course
            message = f"{student.first_name} {student.last_name} has submitted the form '{form.title}'."
            TeacherNotificationDashBoard.objects.create(
                teacher=teacher,
                message=message,
                created_at=now(),
                is_read=False  # Initially unread
            )


        messages.success(request, f"Test submitted successfully! Your score: {total_score}")
        return redirect('std_events')

    except Student.DoesNotExist:
        messages.error(request, "Student not found.")
        return redirect('std_events')

    except Form.DoesNotExist:
        messages.error(request, "Form not found.")
        return redirect('std_events')

    except FormAccessControl.DoesNotExist:
        messages.error(request, "You do not have access to this test.")
        return redirect('std_events')

    except Question.DoesNotExist:
        messages.error(request, "One or more questions not found.")
        return redirect('std_events')

    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        return redirect('std_events')
    

