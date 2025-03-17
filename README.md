# EduConnect – Comprehensive E-Learning Platform  

EduConnect is a next-generation e-learning platform designed to provide a seamless and interactive learning experience. Built with **Django** and **Bootstrap**, EduConnect enables students and teachers to engage in structured online learning with real-time communication, course management, and analytics.

---

## 🚀 Key Functionalities  

### 1. **User Authentication and Role-Based Access**  
- Secure login and registration for students and teachers.  
- OTP-based authentication for enhanced security.  
- Role-based access to control permissions and visibility.  

---

### 2. **Student Dashboard**  
**Overview:** A personalized dashboard providing insights into student performance and activities.  
- **Performance Analytics:**  
   - Graphs showing course completion rates, test scores, and webinar attendance.  
- **Quick Access:**  
   - Access to ongoing courses, assignments, and upcoming events.  

---

### 3. **Course Management**  
#### **Student Side:**  
- View all enrolled courses with real-time progress tracking.  
- Submit assignments and receive feedback from instructors.  
- Access course content (videos, PDFs, and notes).  
- Communicate with instructors via the course forum.  

#### **Teacher Side:**  
- Create, update, and delete course content.  
- Add assignments and configure due dates.  
- Control course visibility and enrollment limits.  

---

### 4. **Assignment Handling**  
#### **Student:**  
- Submit assignments directly through the platform.  
- Get real-time feedback and rework requests.  

#### **Teacher:**  
- Grade assignments and provide feedback.  
- Allow retakes or lock submissions based on completion status.  

---

### 5. **Live Webinars**  
- **Schedule Webinars:**  
   - Teachers can schedule live webinars and notify students.  
   - Students can join webinars directly from the dashboard.  
- **Automatic Attendance Tracking:**  
   - Attendance is automatically logged upon joining.  
   - Teacher can review attendance records.  

---

### 6. **Event Management**  
- Students and teachers can create and join events.  
- Events have defined start and end times.  
- Automatic event reminders and attendance tracking.  

---

### 7. **Certification**  
- Digital certificates are issued upon course completion.  
- Teachers can review and approve certificates.  
- Certificates are downloadable in PDF format.  

---

### 8. **Communication and Feedback**  
- Real-time messaging between students and teachers.  
- Discussion forums for each course.  
- Students can post questions and instructors can respond.  
- Feedback system for reporting issues and suggestions.  

---

### 9. **AI-Powered Chatbot**  
- AI chatbot (powered by **Langchain** + **Gemini**) for instant help.  
- Provides general guidance without login.  
- Logged-in students and teachers receive role-specific assistance.  

---

### 10. **Payment and Billing**  
- Powered by **Razorpay** for secure transactions.  
- Students can enroll in paid courses.  
- Teachers can view earnings and pay platform fees.  
- Payment history and transaction details are available in the dashboard.  

---

### 11. **Snippet Code Editor**  
- Built-in code editor for students.  
- Supports multiple languages (Python, C, Java, etc.).  
- Real-time execution and debugging.  

---

### 12. **Profile Management**  
#### **Students:**  
- Edit personal details and track progress.  
- Manage email notifications and privacy settings.  

#### **Teachers:**  
- Update personal information and add social links.  
- View earnings and payment details.  
- Manage course visibility and enrollment settings.  

---

### 13. **Discussion and Forum**  
- Students can post queries on course forums.  
- Teachers can respond directly or start discussions.  
- Peer-to-peer interaction is supported.  

---

### 14. **Search and Filtering**  
- Advanced search for courses based on:  
   - Popularity  
   - Category  
   - Instructor Rating  
- Real-time filtering to find relevant content quickly.  

---

### 15. **Data Privacy and Security**  
- User data (email, phone number) is hidden unless shared.  
- GDPR-compliant data handling and encryption.  
- Secure session handling and token-based authentication.  

---

### 16. **Analytics and Insights**  
#### **For Students:**  
- View overall progress, test performance, and completion rates.  
- Compare performance with other students.  

#### **For Teachers:**  
- Track student engagement and performance.  
- View total enrollments and completion rates.  
- Course rating and feedback overview.  

---

## 👨‍🏫 **Teacher Dashboard Features**  

### 1. **Course Control**  
- Create, update, and delete courses.  
- Assign tests and update content dynamically.  
- Manage visibility and student access.  

---

### 2. **Event and Webinar Management**  
- Create events and live sessions.  
- Schedule webinars and track attendance.  
- Control student participation.  

---

### 3. **Certification Control**  
- Issue certificates upon course completion.  
- Review and approve student progress.  
- Generate PDF-based certificates.  

---

### 4. **Payment and Earnings**  
- View earnings and expenses.  
- Pay platform fees and other expenses.  
- Secure Razorpay integration.  

---

### 5. **Discussion and Support**  
- Respond to student queries.  
- Start and moderate course discussions.  
- Monitor course ratings and reviews.  

---

### 6. **Settings and Profile Management**  
- Update personal details.  
- Manage notifications and communication settings.  
- Control public visibility and data handling.  

---

## ✅ **Tech Stack**  
- **Backend:** Django (Python)  
- **Frontend:** HTML, CSS, JavaScript, Bootstrap  
- **AI:** Langchain, Gemini  
- **Database:** PostgreSQL  
- **Payment Gateway:** Razorpay  
- **Authentication:** Django Authentication, OTP Verification  

---

## ✅ **Deployment**  
- Deployed on **AWS** (or preferred cloud platform).  
- CI/CD pipeline for automated deployment and testing.  

---

## 💡 **Future Scope**  
- AI-based learning recommendations.  
- Integration with third-party LMS tools.  
- Offline content access and mobile app support.  

---

## 📥 **Setup and Installation**  

**1. Clone the Repository:**  
Clone the repository from GitHub using the following command:  
```bash  
git clone https://github.com/amar-verma/EduConnect-E-Learning-Platform.git  
```  

**2. Navigate to the Project Directory:**  
```bash  
cd EduConnect-E-Learning-Platform  
```  

**3. Install Python:**  
Ensure Python is installed (version 3.8 or higher).  
👉 Download Python from [python.org](https://www.python.org/downloads/).  

**4. Create a Virtual Environment:**  
Create a virtual environment using the following command:  
```bash  
python -m venv env  
```  

Activate the virtual environment:  
- **Windows:**  
```bash  
.\env\Scripts\activate  
```  
- **MacOS/Linux:**  
```bash  
source env/bin/activate  
```  

**5. Add API Keys (for Meeting, Email, and Payment):**  
- Add API keys for **Meeting**, **Email**, and **Razorpay** in the `.env` file.  
- Create a `.env` file in the root directory and add:  
```bash  
RAZORPAY_API_KEY = 'your_razorpay_key'  
EMAIL_HOST_USER = 'your_email@example.com'  
EMAIL_HOST_PASSWORD = 'your_email_password'  
MEETING_API_KEY = 'your_meeting_api_key'  
```  

**6. Install Dependencies:**  
Find the `requirements.txt` file (located in the root directory) and install all Python packages using:  
```bash  
pip install -r requirements.txt  
```  

**7. Apply Migrations:**  
Make migrations and apply them using the following commands:  
```bash  
python manage.py makemigrations  
python manage.py migrate  
```  

**8. Create Superuser:**  
Create an admin user for accessing the admin panel:  
```bash  
python manage.py createsuperuser  
```  
- Enter the username, email, and password when prompted.  

**9. Run the Development Server:**  
Once everything is set up, start the Django development server:  
```bash  
python manage.py runserver  
```  
Open the browser and visit:  
```
http://127.0.0.1:8000/  
```  

**10. You’re All Set to Go!** 🚀  

---

✅ **Note:**  
- Make sure that the `.env` file is added to `.gitignore` to avoid exposing sensitive information.  

---

### ➡️ **Repository Link:**  
👉 [EduConnect – GitHub Repository](https://github.com/amar-verma/EduConnect-E-Learning-Platform)  

---

### ✅ **Instructions:**  
1. Copy the above section into your `README.md` file.  
2. Adjust the API key details according to your setup.  
3. Commit and push the changes.  

---

This section is clean, professional, and follows GitHub best practices! 😎
