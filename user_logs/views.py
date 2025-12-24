from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from dashboard.models import Board
from dashboard.views import boardPage

from .forms import NewLog

# Create your views here.
@login_required
def newLog(request, id):
    board = get_object_or_404(Board, pk=id)

    if request.method == 'POST':
        form = NewLog(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.board = board
            log.save()
            return redirect(boardPage, id=id)
        else:
            print(form.errors)
    else:
        form = NewLog()

    return render(request, 'logs/newLog.html', {'form' : form, 'board' : board})