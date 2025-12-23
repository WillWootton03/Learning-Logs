from django.shortcuts import render

# Create your views here.
def home(request):
    user = request.user
    if user.is_authenticated:
        context ={
            'user' : user
        }
    else:
        context = None
    return render(request, 'dashboard/home.html', context=context)