from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Board

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

@login_required
def boards(request):
    user = request.user
    boards = Board.objects.filter(user=user.id)
    if not boards.exists():
        boards = None
    context = {
        'user' : user,
        'boards' : boards,
    }
    return render(request, 'dashboard/boards.html', context=context)