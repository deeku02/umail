from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User

class UserRegistrationForm(ModelForm):
    class Meta:
        model=User
        fields=('username','email','password')

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Enter email or username'}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
    )