import os
import subprocess
import random
import string
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt



@csrf_exempt
def submit_code(request):
    if request.method == 'POST':
        language = request.POST.get('language', '').lower()
        code = request.POST.get('code', '')

        if not language or not code:
            return JsonResponse({"error": "Language and code are required."}, status=400)

        # Generate a random file name
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))
        file_path = f"temp/{random_string}.{language}"

        # Create the temporary directory if it doesn't exist
        os.makedirs("temp", exist_ok=True)

        # Write the code to a file
        with open(file_path, "w") as program_file:
            program_file.write(code)

        try:
            if language == "php":
                # Replace the path with your PHP executable path
                output = subprocess.run(["php", file_path], capture_output=True, text=True)
                return JsonResponse({"output": output.stdout or output.stderr})

            elif language == "python":
                # Replace the path with your Python executable path
                output = subprocess.run(["C:\\Users\\Administrator\\AppData\\Local\\Programs\\Python\\Python313\\python.exe", file_path], capture_output=True, text=True)
                return JsonResponse({"output": output.stdout or output.stderr})

            elif language == "node":
                js_file_path = file_path + ".js"
                os.rename(file_path, js_file_path)
                output = subprocess.run(["node", js_file_path], capture_output=True, text=True)
                return JsonResponse({"output": output.stdout or output.stderr})

            elif language == "c":
                output_exe = f"temp/{random_string}.exe"
                subprocess.run(["gcc", file_path, "-o", output_exe], check=True)
                output = subprocess.run([output_exe], capture_output=True, text=True)
                return JsonResponse({"output": output.stdout or output.stderr})

            elif language == "cpp":
                output_exe = f"temp/{random_string}.exe"
                subprocess.run(["g++", file_path, "-o", output_exe], check=True)
                output = subprocess.run([output_exe], capture_output=True, text=True)
                return JsonResponse({"output": output.stdout or output.stderr})

            else:
                return JsonResponse({"error": "Unsupported language."}, status=400)

        except subprocess.CalledProcessError as e:
            return JsonResponse({"error": f"Compilation/Execution error: {e.stderr}"}, status=500)

        except Exception as e:
            return JsonResponse({"error": f"Internal server error: {str(e)}"}, status=500)

        finally:
            # Clean up the temporary files
            if os.path.exists(file_path):
                os.remove(file_path)
            if language in ["c", "cpp"] and os.path.exists(output_exe):
                os.remove(output_exe)

    return JsonResponse({"error": "Only POST method is allowed."}, status=405)

submit_code()
