from django import forms
from captcha.fields import CaptchaField
 
 
class UserForm(forms.Form):
    username = forms.CharField(label="User name", max_length=128)
    password = forms.CharField(label="Password", max_length=256, widget=forms.PasswordInput)
    captcha = CaptchaField(label='Verification code')

class RegisterForm(forms.Form):
    gender = (
        ('male', "male"),
        ('female', "female"),
    )
    username = forms.CharField(label="User name", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="Password", max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="Confirm Password", max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="E-mail", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    sex = forms.ChoiceField(label='Gender', choices=gender)
    captcha = CaptchaField(label='Verification code')
