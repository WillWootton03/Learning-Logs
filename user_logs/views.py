from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse

from dashboard.models import Board
from dashboard.views import boardPage

import json
from django.http import JsonResponse

from .forms import NewLog
from .models import Log

# Create your views here.
@login_required
def newLog(request, board_id):
    board = get_object_or_404(Board, id=board_id)

    if request.method == 'POST':
        data = json.loads(request.body)
        redirect_url = reverse('boardPage', args=[board_id])
        if 'logTitle' and 'logInput' in data:
            log = Log.objects.create(board=board, title=data.get('logTitle'), content=data.get('logInput'))
            log.save() 
            return JsonResponse({'success' : True, 'redirect_url' : redirect_url })
        
        return JsonResponse({'success' : False})

    return render(request, 'logs/newLog.html', {'board' : board})

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