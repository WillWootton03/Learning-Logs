from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.db.models import Count, Q
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import json, io, base64, urllib

from .models import Board, Concept, Tag, Question
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

            return redirect('conceptPage', board_id = board.id, concept_id= concept.id)
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
def conceptPage(request, board_id, concept_id, session_id = None):
    board = Board.objects.get(id=board_id)
    concept = Concept.objects.get(id=concept_id)

    # If user is editing a concept during a session
    if session_id is not None:
        print(session_id)
    
    # Used to get values for initial render of the page
    availableTags_qs = board.tags.exclude(id__in=concept.tags.all().values_list('id', flat=True))
    availableTags = list(availableTags_qs.values('id','name'))
    conceptTags = list(concept.tags.values("id", "name"))
    availableQuestions = Question.objects.exclude(title__in=concept.questions.all())
    return render(request, 'dashboard/conceptPage.html', {'board' : board, 'concept' : concept, 'availableTags' : availableTags, 'conceptTags' : conceptTags, 'sessionId' : session_id, 'availableQuestions' : availableQuestions})

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
            if 'questions' in data:
                questions = Question.objects.filter(title__in=data['questions'])
                concept.questions.set(questions)

            if 'sessionId' in data is not None:
                return redirect('study_session:sessionPage', board.id, data['sessionId'])

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
    sessions = board.sessions.order_by('-dateAdded')

    knownConcepts=Concept.objects.filter(board=board, known=True)
    unknownConcepts=Concept.objects.filter(board=board, unknown=True)
    learningConcepts=Concept.objects.filter(board=board, known=False, unknown=False)
    conceptsCount = len(Concept.objects.filter(board=board))
    tagsCount = len(Tag.objects.filter(board=board))

    graphLabels = ['Known Concepts', 'Learning Concepts', 'Unknown Concepts']
    graphValues = [knownConcepts.count(), learningConcepts.count(), unknownConcepts.count()]
    barColors = ['#22d628','#d6c722','#bf2424']

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(graphLabels, graphValues, color=barColors)

    for tick in ax.get_xticklabels():
        tick.set_fontsize(10)
        tick.set_fontweight('bold')
    fig.patch.set_alpha(0.0)
    ax.set_facecolor('none')

    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = "data:image/png;base64," + urllib.parse.quote(string)


    return render(request, 'dashboard/boardPage.html', {'board' : board, 'logs' : logs, 'knownConcepts' : knownConcepts, 'unknownConcepts' : unknownConcepts, 'learningConcepts' : learningConcepts, 'chart' : uri, 'sessions' : sessions, 'conceptsCount' : conceptsCount, 'tagsCount' : tagsCount })


@login_required
def loadConceptsCSV(request, board_id):
    board = Board.objects.get(id=board_id)
    if request.method =='POST':
        if request.POST.get('confirm') == 'true':
            loadConcepts = [json.loads(concept) for concept in request.POST.getlist('newConcepts')]

            allTags = Tag.objects.filter(board=board)
            allQuestions = Question.objects.all()

            for concept in loadConcepts:
                conceptObject = Concept.objects.create(answer=concept['answer'], definition=concept['definition'], hint=concept['hint'], board=board)
                conceptObject.tags.set(tag for tag in allTags if tag.name in concept['tags'])
                conceptObject.questions.set(question for question in allQuestions if question.title in concept['questions'])

            return JsonResponse({'success' : True})

        if request.FILES.get('file'):
            uploadedFile = io.TextIOWrapper(request.FILES['file'].file, encoding='utf-8')
            reader = csv.DictReader(uploadedFile)

            newConceptsCount = 0
            newTags = set()
            concepts = []
            existingTags = set(tag.name for tag in Tag.objects.filter(board=board))
            if reader:
                #Only Appends New Concepts to Concept Model
                for row in reader:
                    if not any(row):
                        continue
                    
                    answer = row['Answer']
                    definition = row['Definition']
                    hint = row['Hint']
                    questions = ['answer']
                    tags = {tag.strip() for tag in row['Tags'].split(',')}
                    if row.get('Questions', '').strip():
                        questions = [question.strip() for question in row.get('Questions', '').split(',')]
                    
                    newTags.update(tag for tag in tags if tag not in existingTags)
                    # Checks for tags in the tag field of file, if tag doesn't exsist creates a new tag and adds it to tags
                    
                    # Checks for concept matching when uploading new files
                    if not Concept.objects.filter(answer=answer, definition=definition, hint=hint, board=board).exists():
                        concepts.append({'answer' : answer, 'definition' : definition, 'hint': hint, 'tags' : list(tags), 'questions' : questions})
                        newConceptsCount += 1
                return JsonResponse({'success': True, 'newConcepts' : concepts, 'newTags': list(newTags), 'newConceptsCount' : newConceptsCount})

        return JsonResponse({'success' : False})

import csv
import io
@login_required
def fileUpload(request, board_id):
    data = json.loads(request.body)
    board = Board.objects.get(id=board_id)
    if data:
        if 'newTags' in data:
            for tagName in data['newTags']:
                Tag.objects.create(name=tagName, board=board)
        if 'newConcepts' in data:
            for concept in data['newConcepts']:
                concept = Concept.objects.create(board=board, answer=concept, definition=concept['definition'], hint=concept['hint'])
                concept.tags.set(concept['tags'])
                concept.questions.set(concept['questions'])

    return redirect('boardPage', board_id)

@login_required
@require_POST
def deleteBoard(request):
    boardId= request.POST.get('board_id')
    board = Board.objects.get(id=boardId)
    if board:
        board.delete()
    return redirect('dashboard')

@login_required
def deleteAllConcepts(request, board_id):
    board = Board.objects.get(id=board_id)
    board.concepts.all().delete()
    return redirect('boardPage', board_id)

@login_required
def deleteAllTags(request, board_id):
    board = Board.objects.get(id=board_id)
    board.tags.all().delete()
    return redirect('boardPage', board_id)