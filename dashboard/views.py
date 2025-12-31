from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.db.models import Count, Q

import json

from .models import Board, Concept, Tag
from user_logs.models import Log
from study_session.models import Session

from .forms import NewBoard, CreateTag, NewConcept


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
    # Makes it so only one query is used when searching for counts instead of using for loop
    # VERY IMPORTANT makes lookup time scale better
    boards = Board.objects.filter(user=request.user).annotate(
        knownCount=Count('concepts', filter=Q(concepts__known=True), distinct=True),
        unknownCount=Count('concepts', filter=Q(concepts__unknown=True), distinct=True),
        learningCount=Count('concepts', filter=Q(concepts__known=False, concepts__unknown=False), distinct=True),
        logCount=Count('logs', distinct=True),
    )
        

    context = {
        'user' : user,
        'boards' : boards
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
def newConcept(request, board_id):
    board = Board.objects.get(id=board_id)

    if request.method == 'POST':
        form = NewConcept(request.POST)
        if form.is_valid():
            concept = form.save(commit=False)
            concept.board = board
            concept.save()

            return redirect('boardPage', board_id = board.id)
    else:
        form = NewConcept()

    return render(request, 'dashboard/newConcept.html', {'board' : board, 'form' : form})

@login_required
def createTag(request, board_id):
    board = Board.objects.get(id=board_id)
    if request.method == 'POST':
        data = json.loads(request.body)
        tag = Tag()
        tag.board = board
        if 'name' in data:
            tag.name = data['name']
        
        tag.save()

        return JsonResponse({'success' : True, 'name' : tag.name, 'id' : tag.id })


@login_required
def conceptPage(request, board_id, concept_id):
    board = Board.objects.get(id=board_id)
    concept = Concept.objects.get(id=concept_id)
    
    # Used to get values for initial render of the page
    availableTags_qs = board.tags.exclude(id__in=concept.tags.all().values_list('id', flat=True))
    availableTags = list(availableTags_qs.values('id','name'))
    conceptTags = list(concept.tags.values("id", "name"))
    return render(request, 'dashboard/conceptPage.html', {'board' : board, 'concept' : concept, 'availableTags' : availableTags, 'conceptTags' : conceptTags})

@login_required
def conceptToggleTags(request, board_id, concept_id, tag_id):
    board = Board.objects.get(id=board_id)
    concept = Concept.objects.get(id=concept_id)
    tag = Tag.objects.get(id=tag_id)

    if tag in concept.tags.all():
        concept.tags.remove(tag)
    else:
        concept.tags.add(tag)

    #Updates tag boxes
    conceptTags = list(concept.tags.values('id', 'name'))
    availableTags = list(board.tags.exclude(id__in=concept.tags.all().values_list('id', flat=True)).values('id','name'))

    return JsonResponse({'conceptTags' : conceptTags, 'availableTags' : availableTags})

@require_POST
@login_required
def deleteTag(request, tag_id):
    try:
        tag = Tag.objects.get(id=tag_id)
        tag.delete()
        return JsonResponse({'success' : True})
    except Tag.DoesNotExist:
        return JsonResponse({'success' : False, 'error' : 'Tag not found'}, status=404)

@csrf_exempt
@login_required
def updateConcept(request, concept_id):
    if request.method == 'POST':
            data = json.loads(request.body)
            concept = Concept.objects.get(id=concept_id)
            board = concept.board

            if 'answer' in data:
                concept.answer = data['answer']
            if 'definition' in data:
                concept.definition = data['definition']
            if 'hint' in data:
                concept.hint = data['hint']
            concept.save()

            if 'tags' in data:
                tags = Tag.objects.filter(id__in=data['tags'])
                concept.tags.set(tags)


            return JsonResponse({'success' : True})

@require_POST
@login_required
@csrf_exempt
def deleteConcept(request, concept_id):
    concept = get_object_or_404(Concept, id=concept_id)

    boardId = concept.board.id
    concept.delete()

    return redirect('boardPage', boardId)

@login_required
def boardPage(request, board_id):
    board = Board.objects.get(id=board_id)
    logs = board.logs.all().order_by('-dateAdded')


    knownConcepts=Concept.objects.filter(board=board, known=True)
    unknownConcepts=Concept.objects.filter(board=board, unknown=True)
    learningConcepts=Concept.objects.filter(board=board, known=False, unknown=False)
    

    return render(request, 'dashboard/boardPage.html', {'board' : board, 'logs' : logs, 'knownConcepts' : knownConcepts, 'unknownConcepts' : unknownConcepts, 'learningConcepts' : learningConcepts })

import csv
import io
@login_required
@require_POST
def uploadConceptsCSV(request, board_id):
    board = Board.objects.get(id=board_id)
    if request.method == 'POST' and request.FILES.get('concept-file'):
        uploadedFile = io.TextIOWrapper(request.FILES['concept-file'].file, encoding='utf-8')
        reader = csv.DictReader(uploadedFile)
        if reader:
            print('reader')
        #Only Appends New Concepts to Concept Model
        for row in reader:
            if not any(row):
                continue
            answer = row['Answer']
            definition = row['Definition']
            hint = row['Hint']
            tags = [tag.strip() for tag in row['Tags'].split(',') if tag.strip()] 
            print(answer)

            existingTags = {tag.name: tag for tag in Tag.objects.all()}

            tagObjects = []
            for tagName in tags:
                if tagName in existingTags:
                    tagObjects.append(existingTags[tagName])
                else:
                    newTag = Tag.objects.create(name=tagName, board=board)        
                    existingTags[tagName] = newTag
                    tagObjects.append(newTag)

            if not Concept.objects.filter(answer=answer, definition=definition, hint=hint).exists():
                print(answer)
                concept = Concept.objects.create(board=board, answer=answer, definition=definition, hint=hint)
                concept.tags.set(tagObjects)

        return redirect('boardPage', board_id)

    return redirect('boardPage', board_id)
