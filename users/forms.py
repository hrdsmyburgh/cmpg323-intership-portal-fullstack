from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Student

class UserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "role")

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "student_id",
            "degree",
            "year_of_study",
            "cv",
        ]
