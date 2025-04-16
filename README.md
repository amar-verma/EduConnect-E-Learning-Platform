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
x-rapidapi-key: " # Replace with valid API key"
x-rapidapi-host: " # Replace with valid API host key"
genai.configure(api_key="Replace with gemini api key")
serverSecret = "Replace with ZegoUIKitPrebuilt api key"

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
