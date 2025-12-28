from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import Board, Concept
from user_logs.models import Log
from study_session.models import Session

from .forms import NewBoard, SetTags, NewConcept


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
    boards = user.boards.all()
    if not boards.exists():
        boards = None
    context = {
        'user' : user,
        'boards' : boards,
    }
    return render(request, 'dashboard/boards.html', context=context)

@login_required 
def newBoard(request):
    user = request.user
    
    options = {
        5 : 'Quick Memorization',
        10 : 'Some Memorization',
        15 : 'Slightly Below Reccommended',
        20 : 'Reccommended Amount for Memorization',
        25 : 'Really Remember Something',
        30 : 'Fully Understand a Concept'
    }

    if request.method == 'POST':
        form = NewBoard(request.POST)
        if form.is_valid():
            board = form.save(commit=False)
            board.knownThreshold = int(request.POST.get('dropdown-value', 5))
            board.user = user
            board.save()
            print(f'Saved Board: {board.title}, id={board.id}, user={board.user}, knownThreshold={board.knownThreshold}')

            return redirect('home')
        else:
            print(form.errors)
    else:
        form = NewBoard()


    return render(request, 'dashboard/newBoard.html', {'form' : form, 'options' : options, 'user' : user})

@login_required
def newConcept(request, id):
    board = Board.objects.get(id=id)

    if request.method == 'POST':
        form = NewConcept(request.POST)
        if form.is_valid():
            concept = form.save(commit=False)
            concept.board = board
            concept.save()

            return redirect('setTags', board_id = board.id, concept_id=concept.id)
    else:
        form = NewConcept()

    return render(request, 'dashboard/newConcept.html', {'board' : board, 'form' : form})

@login_required
def setTags(request, board_id, concept_id):
    board = Board.objects.get(id=board_id)
    concept = Concept.objects.get(id=concept_id)
    if request.method == 'POST':
        form = SetTags(request.POST)
        if form.is_valid():
            tag = form.save(commit=False)
            tag.board = board
            tag.concept = None
            tag.save()
            #CHANGE TO CONCEPT PAGE FOR SPECIFIC CONCEPT
            return redirect('setTags', board_id=board.id, concept_id=concept.id)
    else:
        form = SetTags()

    return render(request, 'dashboard/setTags.html', {'form' : form, 'board' : board, 'concept' : concept})

@login_required
def boardPage(request, id):
    board = Board.objects.get(id=id)
    logs = board.logs.all().order_by('-dateAdded')
    return render(request, 'dashboard/boardPage.html', {'board' : board, 'logs' : logs})