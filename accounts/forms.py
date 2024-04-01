from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.db import transaction
from .models import *
from django import forms
from django.contrib.auth import get_user_model
from .models import EquipmentTable


User = get_user_model()


class MemberSignUpForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control radius-30 ps-5"}), label=("Email"))
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control radius-30 ps-5"}), label=("Username"))
    password1 = forms.CharField(label=("Password"), widget=forms.PasswordInput(attrs={"class": "form-control radius-30 ps-5"}))
    password2 = forms.CharField(label=("Confirm Password"), widget=forms.PasswordInput(attrs={"class": "form-control radius-30 ps-5"}))

    first_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control radius-30 ps-5"}), label="First Name")
    last_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control radius-30 ps-5"}), label="Last Name")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')
    
    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_member = True
        if commit:
            user.save()
        client = Member.objects.create(user=user, first_name=self.cleaned_data.get('first_name'), last_name=self.cleaned_data.get('last_name'))
        return user
    


class ManagementSignUpForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control radius-30 ps-5"}), label=("Email"))
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control radius-30 ps-5"}), label=("Username"))
    password1 = forms.CharField(label=("Password"), widget=forms.PasswordInput(attrs={"class": "form-control radius-30 ps-5"}))
    password2 = forms.CharField(label=("Confirm Password"), widget=forms.PasswordInput(attrs={"class": "form-control radius-30 ps-5"}))

    first_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control radius-30 ps-5"}), label="First Name")
    last_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control radius-30 ps-5"}), label="Last Name")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')
    
    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_management = True
        if commit:
            user.save()
        personell = InstructorTable.objects.create(user=user, first_name=self.cleaned_data.get('first_name'), last_name=self.cleaned_data.get('last_name'))
        return user
    
    
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control radius-30 ps-5"}), label=("Username"))
    password = forms.CharField(label=("Password"), widget=forms.PasswordInput(attrs={"class": "form-control radius-30 ps-5"}))
   



class OnDemandWorkoutForm(forms.ModelForm):
    class Meta:
        model = OnDemandWorkoutTable
        fields = ['title', 'description', 'video_url', 'duration']
        
class GymClassForm(forms.ModelForm):
    class Meta:
        model = GymClass
        fields = ['class_name', 'instructor', 'description', 'day', 'start_time', 'end_time', 'capacity', 'status', 'charged_amount']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['video_id', 'title', 'description']





class EquipmentForm(forms.ModelForm):
    class Meta:
        model = EquipmentTable
        fields = '__all__'