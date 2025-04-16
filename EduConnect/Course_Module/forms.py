from django import forms
from .models import CourseComment
from django.contrib.auth.forms import UserCreationForm
from Edu_Main.models import User

class CourseCommentForm(forms.ModelForm):
    class Meta:
        model = CourseComment
        fields = ["comment", "value"]  # Users can enter text & like/dislike course
        widgets = {
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Write your feedback..."}),
        }


class StudentRegistrationForm(UserCreationForm):
    gender = forms.ChoiceField(choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")], required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username, user_type='student').exists():
            raise forms.ValidationError("A student with this username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email, user_type='student').exists():
            raise forms.ValidationError("A student with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'student'
        if commit:
            user.save()
        return user