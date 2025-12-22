from django.shortcuts import render

# Create your views here.
def home(request):
     return render(request, 'home.html')

def signIn(request):
     return render(request, 'authentication/signIn.html')

def register(request):
     return render(request, 'authentication/register.html')

def boards(request):
     return render(request, 'dashboard/boards.html')