from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class TeacherSignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 2
        if commit:
            user.save()
        return user

class StudentSignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 3
        if commit:
            user.save()
        return user


from .models import Course

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'price', 'thumbnail', 'level']

from django import forms
from .models import Course, CustomUser

class ManagerCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'price', 'thumbnail', 'level', 'teacher']

    teacher = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(user_type=2),
        label="Assign Teacher"
    )
