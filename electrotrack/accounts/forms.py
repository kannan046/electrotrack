from django import forms
from django.contrib.auth import get_user_model
from .models import User, WorkReport, MaterialRequest



User = get_user_model()


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Password'
    }))


class UserForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 'placeholder': 'New password (optional)'
        })
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]
        widgets = {
            "username": forms.TextInput(attrs={'class': 'form-control'}),
            "email": forms.EmailInput(attrs={'class': 'form-control'}),
        }


class WorkReportForm(forms.ModelForm):
    class Meta:
        model = WorkReport
        fields = ['task_name', 'description', 'hours_worked', 'status']  

        

class MaterialRequestForm(forms.ModelForm):
    class Meta:
        model = MaterialRequest
        fields = ["item_name", "quantity", "description",'photo']
          
