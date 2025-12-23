from django import forms
from django.forms.models import ModelForm

from .models import User

class RegisterForm(forms.ModelForm):
    verifyPassword = forms.CharField(widget=forms.PasswordInput(attrs={
                'placeholder' : 'Password',
                'required' :True,
                'id' : 'verify-password',
                'class' : "w-full rounded-md bg-white/5 px-3 py-2 pr-10 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
            }))
    class Meta:
        model = User
        fields = ['email', 'username', 'password']
        widgets = {
            'email' : forms.EmailInput(attrs={
                'placeholder': 'email@example.com',
                'required' : True,
                'id' : 'email',
                'class' : "block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 focus:outline-purple-500 sm:text-sm/6"
            }),
            'username' : forms.TextInput(attrs={
                'placeholder' : 'Username',
                'required': True,
                'id' : 'username',
                'class' : "block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 focus:outline-purple-500 sm:text-sm/6" 
            }),
            'password' : forms.PasswordInput(attrs={
                'placeholder' : 'Password',
                'required' :True,
                'id' : 'password',
                'class' : "w-full rounded-md bg-white/5 px-3 py-2 pr-10 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        verifyPassword = cleaned_data.get('verify-password')
        if password and verifyPassword and password != verifyPassword:
            raise forms.ValidationError('Passwords do not match')
        return cleaned_data
    
class SignInForm(forms.Form):
        email = forms.EmailField(
            widget=forms.TextInput(attrs={
                'placeholder' : 'example@email.com',
                'required': True,
                'id' : 'email',
                'name': 'email',
                'class' : "block w-full rounded-md bg-white/5 px-3 py-2 text-base text-white outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 focus:outline-purple-500 sm:text-sm/6" 
            }))
        password = forms.CharField(
            widget=forms.PasswordInput(attrs={
                'placeholder' : 'Password',
                'required' :True,
                'name' : 'password',
                'id' : 'password',
                'class' : "w-full rounded-md bg-white/5 px-3 py-2 pr-10 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
            }))