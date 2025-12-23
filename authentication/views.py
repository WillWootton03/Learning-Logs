from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from .forms import RegisterForm, SignInForm

from .models import User


# Create your views here.
def home(request):
     return render(request, 'home.html')

def signIn(request):
     if request.method == 'POST':
          form = SignInForm(request.POST)
          if form.is_valid():
               email = form.cleaned_data['email']
               password = form.cleaned_data['password']

               user = authenticate(request, username=email, password=password)
               if user is not None:
                    login(request, user)
                    return redirect('home')
               else:
                    form.add_error(None, 'Invalid Username or password')
     else:
          form = SignInForm()

     return render(request, 'authentication/signIn.html', {'form': form})

def register(request):
     if request.method == 'POST':
          form = RegisterForm(request.POST)
          if form.is_valid():
               user = form.save(commit=False)
               user.set_password(form.cleaned_data['password'])
               user.email = form.cleaned_data['email']
               user.username = form.cleaned_data['username']

               user.save()

               return redirect('/signIn/')
     else:
          form = RegisterForm()

     return render(request, 'authentication/register.html', {'form': form})
