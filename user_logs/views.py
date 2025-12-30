from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from dashboard.models import Board
from dashboard.views import boardPage

from .forms import NewLog
from .models import Log

# Create your views here.
@login_required
def newLog(request, board_id):
    board = get_object_or_404(Board, id=board_id)

    if request.method == 'POST':
        form = NewLog(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.board = board
            log.save()
            return redirect(boardPage, board_id=board_id)
        else:
            print(form.errors)
    else:
        form = NewLog()

    return render(request, 'logs/newLog.html', {'form' : form, 'board' : board})

@login_required
def logBreakdown(request, log_id):
    log = Log.objects.get(id=log_id)
    return render(request, 'logs/logBreakdown.html', {'log' : log, 'board' : log.board })

@login_required
@require_POST
def deleteLog(request, log_id):
    log = Log.objects.get(id=log_id)
    board = log.board
    if log:
        log.delete()
    return redirect(boardPage, board_id=board.id)