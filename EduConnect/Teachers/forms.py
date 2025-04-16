from django import forms
from .models import Teacher
import re

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['first_name', 'last_name', 'profile_picture', 'phone_number', 'address', 'city', 'state', 'country', 'bio', 'social_links']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'address': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }

    first_name = forms.CharField(required=True, max_length=100)
    last_name = forms.CharField(required=True, max_length=100)
    profile_picture = forms.ImageField(required=True)
    phone_number = forms.CharField(required=True, max_length=15)
    address = forms.CharField(required=True, max_length=255)
    city = forms.CharField(required=True, max_length=50)
    state = forms.CharField(required=True, max_length=50)
    country = forms.CharField(required=True, max_length=50)
    bio = forms.CharField(required=True, max_length=500)  
    social_links = forms.CharField(required=False, max_length=500)  

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        phone_number = re.sub(r'\D', '', phone_number)
        if len(phone_number) != 10 or not phone_number.isdigit():
            raise forms.ValidationError("Phone number must be exactly 10 digits and contain only numbers.")
        return phone_number



