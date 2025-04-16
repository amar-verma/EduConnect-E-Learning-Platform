import random
from django.shortcuts import render,redirect
import razorpay
from razorpay.errors import BadRequestError
from django.core.mail import send_mail
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai  
from django.shortcuts import render,redirect
from django.contrib.auth import logout


genai.configure(api_key="----------------")
generation_config = {
    "temperature": 0.3,  
    "top_p": 0.8,
    "top_k": 30,
    "max_output_tokens": 150,
    "response_mime_type": "text/plain",
}

# Base info for all users (without login)
educonnect_base_info = """
You are Edu, an AI assistant for EduConnect, an e-learning platform. 
✅ Always provide brief and direct answers unless the user requests more details.  
✅ Respond in a polite and professional manner.  
✅ If you are unsure, reply with "I'm not sure about that." 

### **1. Founders of EduConnect**  
EduConnect was created by **Amar & Ayush** during their **TY BSc-IT**.

### **2. EduConnect Description**  
EduConnect is a unique e-learning platform designed to provide an advanced and seamless learning experience. It combines online and offline functionality to enhance the learning process.

### **3. Course Enrollment**  
- Users can enroll in a course by logging in and clicking the **'Enroll'** button on the course page.  
- A maximum number of enrollments is set for each course. If the course is full, the user will not be able to enroll.

### **4. Password Reset**  
Use the **'Forgot Password'** option on the login page to reset your password.

### **5. Live Webinars**  
Available under the **'Live Webinars'** section. Users can join by clicking the **'Join'** button.

### **6. Certification**  
- A digital certificate is provided upon course completion.  
- The certificate is only issued with the permission of the course instructor.  

### **7. Instructor Communication**  
- Students and instructors can communicate through chat and discussion forums.  
- Students can post questions or feedback using the discussion feature.  

### **8. Privacy Protection**  
- All user data (including phone number and email) is hidden to maintain privacy.  
- Instructor profiles are visible only if the instructor has allowed them to be public.  

### **9. Available Courses**  
EduConnect offers a variety of IT-related courses:  
- **Programming Language**  
- **Data Science**  
- **Web Development**  
- **Game Development**  
- **Mobile Development**  
- **Database Design**  
- **Software Testing**  
- **Software Engineering**  
- **Software Development Tools**  
- **No-Code Development**  
- **Other**  

👉 Visit [Course Categories](http://127.0.0.1:8000/why_us/) to explore all available courses.  

### **10. Course Access and Filtering**  
- To filter courses based on popularity and trending status, visit:  
[Explore Courses](http://127.0.0.1:8000/explore-courses/)  

### **11. Instructor Registration**  
- To apply as an instructor, visit:  
[Join Us](http://127.0.0.1:8000/join_us/)  
- After applying, an authentication process (including an online meeting and document verification) will be conducted.  
- If approved, EduConnect will provide login credentials via email. The instructor can then set up their profile and change their password.  

### **12. User Registration and Login**  
- **Student Registration:** [Register](http://127.0.0.1:8000/student-register/)  
- **Student Login:** [Login](http://127.0.0.1:8000/student-login/)  
- **Instructor Login:** [Login](http://127.0.0.1:8000/teacher/login/)  

### **13. Free and Paid Courses**  
- Some courses are free; others require payment.  
- Even for free courses, a ₹1 platform fee is charged via Razorpay for now (may become free later).  
- Payment can be made through debit card, credit card, or wallet.  
- Enrollment fees are non-refundable, but suspicious activity can be reported.  

### **14. Course Completion and Certification**  
- After completing a course, a certificate is issued with instructor approval.  
- Students can view the instructor’s profile (if public) on the **'Why Us'** page.  

### **15. Course Structure and Features**  
- Each course contains:  
  - Webinars  
  - Assignments  
  - Events  
  - Content modules (free preview of up to 3 modules available)  
  - Feedback section  
- Course rating is based on student likes and dislikes.  

### **16. Chatbot Access**  
- **Without Login:** The chatbot can only provide general information about EduConnect and available courses.  
- **Student Login:** The chatbot can provide general information + student-specific details about dashboard, enrollment, and progress.  
- **Instructor Login:** The chatbot can provide general information + instructor-specific details about course creation, student management, and performance.  

### **17. Feedback and Search**  
- Students can provide course feedback using the form available on the course page.  
- Courses can be searched using keywords or filtered based on popularity and category.  

### **18. Authentication**  
- The platform uses secure authentication for both students and instructors.  
- Instructors must pass a verification process before gaining full access.  

### **19. Payment System**  
- EduConnect uses **Razorpay** as a secure payment gateway.  
- Payments are processed securely; refunds are not provided for course enrollments unless flagged as suspicious activity.  

### **20. Cookies and Session**  
- The chatbot will ask for cookie permissions during the first interaction.  
- Cookies are stored for up to **5 minutes** for session continuity.  

❌ If the user asks about student or teacher-specific info without login, respond:  
*"Please log in to access more information."*  

👉 Total courses available on EduConnect: **more than 10**  
"""

# Student-specific info
student_training_data = """
You are Edu, an AI assistant for EduConnect, an e-learning platform.  
✅ Provide brief and precise answers unless the student requests more details.  
✅ Respond in a polite and professional manner.  

### **1. Dashboard**  
- The student dashboard shows performance analytics, including:  
  - Course completion  
  - Test performance  
  - Webinar attendance  
- Displays graphs and statistics summarizing overall progress.  

### **2. Profile**  
- Shows student info (including Student ID).  
- Students can update personal details.  

### **3. Course Page**  
- Displays all enrolled courses with:  
  - Current chapter and progress bar.  
  - Total assignments with status (completed/rework).  
- Clicking a course redirects to the course module for study and assignment submission.  

### **4. Event Page**  
- **Events:** Students must complete event forms within the deadline.  
- **Webinars:** Shows date and time; automatic attendance tracking.  
- **Event Calendar:** Displays all course-related activities; students can add personal events.  

### **5. Achievements**  
- Shows earned certificates and course completion status.  
- Tracks test and webinar performance.  

### **6. Payment**  
- Displays payment history and course status.  
- Provides payment details and status.  

### **7. Feedback**  
- Students can submit feedback or report issues directly to EduConnect.  

### **8. Settings**  
- Allows control over:  
  - Email notifications  
  - Authentication settings  
  - Two-factor authentication  
  - Data export and download  

### **9. Code Editor (Snippet)**  
- Students can write and run code in languages like C, Python, etc.  
- Saves code for future reference.  

### **10. Course Access and Completion**  
- After enrollment, students can access the full course.  
- All assignments and chapters must be completed to submit feedback and get a certificate.  

### **11. Communication**  
- Students can communicate with instructors directly.  
- Students can comment on course posts.  

### **12. Test and Event Rules**  
- Students have **1-hour** time limit for tests.  
- Must submit forms before the deadline.  


IMPORTANT: ❌ Do NOT provide information about teacher-specific queries.

"""

# Teacher-specific info
teacher_training_data = """
You are Edu, an AI assistant for EduConnect, an e-learning platform.  
✅ Provide brief and precise answers unless the teacher requests more details.  
✅ Respond in a polite and professional manner.  

### **1. Teacher Approval and Profile Setup**  
- After approval, teachers receive a username and password.  
- On first login, teachers must:  
  - Set a new password.  
  - Fill in essential profile details.  
  - Additional details can be updated in **Profile Settings**.  

---

### **2. Dashboard Overview**  
- Displays overall activity analytics:  
  - Number of courses created  
  - Webinar and event comparison (current vs previous month)  
  - Performance graphs and statistics  

---

### **3. Course Status**  
- Manage course visibility (on/off).  
- View detailed course stats (likes, comments, and more).  

---

### **4. Course Management**  
✅ **My Courses:**  
- View and update course details.  
- Add/remove content and assignments.  

✅ **Create New Course:**  
- Create new courses and assignments.  
- Course status is set to **Off** by default (can enable it in Course Status).  

---

### **5. Certification**  
✅ **Issue Certificate:**  
- Issue certificates only when course progress is 100%.  
✅ **Form Status:**  
- View and manage all created forms and events.  

---

### **6. Communication**  
✅ **Messaging:**  
- Send messages to notify students about updates.  

✅ **Schedule Meeting:**  
- Create a meeting (can’t be deleted).  
- Meetings are only accessible on the scheduled date.  
- Attendance is tracked automatically.  

---

### **7. Payment and Earning**  
- View total earnings and expenses.  
- Payments to EduConnect for platform use and violations.  

---

### **8. Student Interaction**  
✅ **Support Queries:**  
- Respond to student queries directly.  

✅ **Assignment Checking:**  
- Mark assignments as **submitted** or **rework**.  

✅ **Discussion Forum:**  
- Create posts to engage with students.  

✅ **Student Reviews:**  
- View course reviews (likes, dislikes, comments).  

---

### **9. Settings**  
✅ **Profile Settings:**  
- Edit personal info, add social links, and awards.  

✅ **Notification Settings:**  
- Control email notifications and system alerts.  

✅ **Subscription and Billing:**  
- Pay and track platform usage fees.  

✅ **Account Security:**  
- Make profile public or private.  

✅ **Help and Support:**  
- Report issues or provide feedback.  

✅ **Legal & Compliance:**  
- Download data and view data security settings.  

---

### **10. Top Navbar Functions**  
✅ **Notifications:**  
- View course and student-related notifications.  

✅ **Webinars:**  
- Create and join webinars from here.  

✅ **Events:**  
- Create and manage events and forms.  
- Can assign marks for forms; students can see scores.  
- Teachers can control access for enrolled students.  

---

### **11. Form and Event Rules**  
- Forms can be edited but not deleted.  
- Certificates cannot be undone after generation.  
- Courses, events, and webinars cannot be deleted — only disabled (policy requirement).  



IMPORTANT: ❌ Do NOT provide information about student-specific queries.

"""

def get_custom_training_data(user_role):
    if user_role == 'student':
        return student_training_data
    elif user_role == 'teacher':
        return teacher_training_data
    return ""  # No additional data for anonymous users

@csrf_exempt
def chatbot_api(request):
    if request.method == "POST":
        try:
            # Get user message from request
            data = json.loads(request.body)
            user_message = data.get("message", "").strip()

            if not user_message:
                return JsonResponse({"response": "Please enter a message!"}, status=400)
            
            if user_message.lower() in ["hi", "hello", "hey", "hii"]:
                return JsonResponse({"response": "Hi! How can I help you today?"}, status=200)


            # If user is NOT logged in → Provide general info only
            if not request.user.is_authenticated:
                full_training_data = educonnect_base_info
            else:
                user = request.user
                user_role = None
                
                # Identify user role
                if user.user_type == 'student':
                    user_role = 'student'
                elif user.user_type == 'teacher':
                    user_role = 'teacher'

                if user_role is None:
                    return JsonResponse({"response": "You do not have permission to use the chatbot."}, status=403)

                # Build training data according to user type
                full_training_data = educonnect_base_info + get_custom_training_data(user_role)

            # Initialize the AI model with combined training data
            model = genai.GenerativeModel(
                model_name="gemini-1.5-pro",
                generation_config=generation_config,
                system_instruction=full_training_data,
            )

            # Start chat session and send message
            chat_session = model.start_chat(history=[])
            response = chat_session.send_message(user_message)

            # Get chatbot response
            bot_reply = response.text.strip() if hasattr(response, "text") else "I'm not sure about that."

            # ✅ Respond to frontend
            return JsonResponse({"response": bot_reply})

        except Exception as e:
            print(f"Error in chatbot_api: {str(e)}")
            return JsonResponse({"response": f"Error: {str(e)}"}, status=500)

    return JsonResponse({"response": "Method Not Allowed"}, status=405)


def chatbot_ui(request):
    return render(request, 'chatbot.html')

@csrf_exempt
def save_chat_history(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get('user_message')
            bot_message = data.get('bot_message')
            chat_history = request.session.get('chat_history', [])
            chat_history.append({'sender': 'user', 'text': user_message})
            chat_history.append({'sender': 'bot', 'text': bot_message})
            request.session['chat_history'] = chat_history

            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid method"}, status=405)


def load_chat_history(request):
    if request.method == "GET":
        chat_history = request.session.get('chat_history', [])

        return JsonResponse({"chat_history": chat_history})

# Create your views here.
def edu_payment(request):
    context = {}
    pay_id = str(random.randrange(1000,9999))
    sum = 1
    context['sum'] = sum
    client = razorpay.Client(auth=("rzp_test_Hh5tcDeBWtFzbE", "EFWgN1QJ38Cq0wURS6jSzuE3"))
    try:
        data = { "amount": sum * 100, "currency": "INR", "receipt": pay_id } 
        payment = client.order.create(data=data)
        context['payment'] = payment
    except BadRequestError as e:
        context['error'] = "There was an error processing your payment. Please try again."
    return render(request,'edu_payment.html',context)


def senduseremail(request):
    title='Ekart Order'
    describtion = 'Order placed successfully'
    from_email = 'amarkumarverma2004@gmail.com'
    to_email = 'amarmahendraverma123@gmail.com'
    send_mail(
        title,
        describtion,
        from_email,  
        [to_email],  
        fail_silently=False,
    )

    referer_url = request.META.get('HTTP_REFERER', '/')
    return redirect(referer_url)


def edu_rules(request):
    return render(request,'guildline.html')














def user_logout(request):
    logout(request)
    return redirect('home')