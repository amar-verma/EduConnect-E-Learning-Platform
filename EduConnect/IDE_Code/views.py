from django.http import JsonResponse
from django.shortcuts import render,redirect
from .api import compile_code_online
from .models import IdeData
from Students.models import Student
import requests
import certifi
import time
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def home(request,id=None):
    context = {}
    try:
        if id:  # If id is passed in the URL
            try:
                data = IdeData.objects.get(id=id)
                context['code'] = data.code
                context['language'] = data.language
                context['title'] = data.title
            except IdeData.DoesNotExist:
                context['message'] = "Data not found"
        else:
            context['message'] = "Welcome to the editor page!"
        return render(request, 'ide_home.html', context)
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('std_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('/')


@login_required
def index(request):
    if request.user.user_type != 'student': 
        messages.error(request, "You must be a student to access this page.")
        return redirect('std_login')
    context = {}
    try:
        student = Student.objects.get(user = request.user)
        data = IdeData.objects.filter(student=student)
        context['data']=data
        return render(request, 'ide_page.html', context)
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('std_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('/')



@login_required
def submit_code(request):
    context = {}  # Initialize the context dictionary
    if request.user.user_type != 'student': 
        messages.error(request, "You must be a student to access this page.")
        return redirect('std_login')
    
    try:
        if request.method == "POST":
            action = request.POST.get("action", "").lower()  # Check if it's "save" or "run"
            title = request.POST.get("save_title", "").strip()
            language = request.POST.get("language", "").lower()
            code = request.POST.get("code", "")

            

            if not language or not code:
                return render(request, "ide_home.html", {"message": "Language and code are required."})
            
            context = {"title": title, "language": language, "code": code}
            student = Student.objects.get(user = request.user)
            # For Save Functionality
            if action == "save":

                if not title:
                    context["message"] = "Title is required to save the code!"
                    return render(request, "ide_home.html", context)
                
                snippet, created = IdeData.objects.update_or_create(
                    student=student, title=title, language=language,
                    defaults={"code": code}
                )
                context["message"] = "Snippet updated successfully!" if not created else "Snippet saved successfully!"
                return render(request, "ide_home.html", context)

            # For Run Functionality
            elif action == "run":
                language_map = {
                    "c": 50,
                    "cpp": 54,
                    "python": 71,
                    "node": 63,
                    "java": 91,
                    "php": 68
                }
                language_id = language_map.get(language)
                if not language_id:
                    return render(request, "ide_home.html", {"error": "Unsupported language."})

                # Optional: stdin and expected output
                stdin = request.POST.get("stdin", "")  
                expected_output = request.POST.get("expected_output", "")


                # Call Judge0 API for execution
                response = compile_code_online(
                    source_code=code,
                    language_id=language_id,
                    stdin=stdin,
                    expected_output=expected_output
                )

                # Get Execution Status
                status_id = response.get("status", {}).get("id", "")
                status_description = response.get("status", {}).get("description", "")
                output = response.get("stdout", "No output")
                error = response.get("stderr", None)  
                compile_output = response.get("compile_output", None)  
                message = response.get("message", None)  
        
                
                # Handle different status cases
                if status_id == 3:  # ✅ Success
                    output_text = output
                    error_text = None
                elif status_id == 4:  # ❌ Wrong Answer
                    output_text = "Output did not match expected output."
                    error_text = f"Expected: {expected_output}, but got: {output}"
                elif status_id == 5 or 6 or 7:  # ⛔ Runtime Errors
                    output_text = None
                    error_text = f"Runtime Error: {error or 'Unknown error occurred.'}"
                elif status_id == 11:  # ⚠️ Compilation Error
                    output_text = None
                    error_text = f"Compilation Error: {compile_output}"
                elif message:  # Other Errors
                    output_text = None
                    error_text = f"Error: {message}"
                else:
                    output_text = "No output"
                    error_text = None

                
                # Prepare context data for rendering
                context = {
                    "language": language,
                    "code": code,
                    "stdin": stdin,
                    "expected_output": expected_output,
                    "output": output_text,
                    "error": error_text,
                    "status": status_description,
                    "finished_at": response.get("finished_at", "N/A"),
                    "created_at": response.get("created_at", "N/A"),
                    "execution_time": response.get("time", "N/A"),
                    "memory_used": response.get("memory", "N/A"),
                }

                return render(request, "ide_home.html", context)

        return render(request, "ide_home.html", {"error": "Only POST method is allowed."})
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('std_login') 
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('std_dashboard')


