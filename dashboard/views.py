from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache
from django.urls import reverse
from django.db.models import Count, Q, Prefetch


import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import json, io, base64, urllib, csv

from .models import Board, Concept, Tag, Question
from user_logs.models import Log
from study_session.models import Session

from .forms import NewBoard, CreateTag, NewConcept


# Create your views here.
@never_cache
def home(request):
    user = request.user
    if user.is_authenticated:
        return redirect ('dashboard')
    return redirect('signIn')

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
@require_POST
def saveBoardSettings(request, board_id):
    board = Board.objects.get(id=board_id)
    if board:
        data = json.loads(request.body)
        if 'defaultQuestions' in data:
            board.defaultQuestions.set(Question.objects.filter(title__in=data.get('defaultQuestions')))
            questions = list(board.defaultQuestions.values_list('title', flat=True))
        return JsonResponse({ 'success' : True , 'questions' : questions})
    return JsonResponse({ 'success' : False })



@login_required
def boardPage(request, board_id):
    board = Board.objects.prefetch_related(
        Prefetch('concepts', to_attr='allConcepts'),
        Prefetch('defaultQuestions', to_attr='boardConcepts'),
        Prefetch('tags', to_attr='allTags')
    ).get(id=board_id)
    logs = board.logs.order_by('-dateAdded')[:50]
    sessions = board.sessions.order_by('-dateAdded')[:20]

    allQuestions = list(Question.objects.all().values_list('title', flat=True))
    boardQuestions = [question.title for question in board.boardConcepts]


    knownConcepts = [concept for concept in board.allConcepts if concept.known ]
    unknownConcepts = [concept for concept in board.allConcepts if concept.unknown]
    learningConcepts = [concept for concept in board.allConcepts if not concept.known and not concept.unknown]

    conceptsCount = len(board.allConcepts)
    tagsCount = len(board.allTags)

    graphLabels = ['Known Concepts', 'Learning Concepts', 'Unknown Concepts']
    graphValues = [len(knownConcepts), len(learningConcepts), len(unknownConcepts)]
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


    return render(request, 'dashboard/boardPage.html', {'board' : board, 'logs' : logs, 'chart' : uri, 'sessions' : sessions,  'knownConceptsCount' : len(knownConcepts), 'learningConceptsCount' : len(learningConcepts), 'unknownConceptsCount' : len(unknownConcepts), 'knownConcepts' : knownConcepts, 'learningConcepts' : learningConcepts, 'unknownConcepts' : unknownConcepts, 'allQuestions' : allQuestions, 'boardQuestions' : boardQuestions, 'conceptsCount' : conceptsCount, 'tagsCount' : tagsCount})


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

    defaultQuestions = list(Question.objects.all().values_list('title', flat=True))

    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        if data:
            board = Board.objects.create(user=request.user)
            board.title = data.get('title')
            board.description = data.get('description')
            board.knownThreshold = data.get('knownThreshold')
            board.save()

            board.defaultQuestions.set(data.get('questions'))
            print(f'Saved Board: {board.title}, id={board.id}, user={board.user}, knownThreshold={board.knownThreshold}')

            return JsonResponse({ 'success' : True,  'redirect_url' : reverse('boardPage', args=[board.id])})
        
    return render(request, 'dashboard/newBoard.html', {'options' : options, 'user' : user, 'allQuestions' : defaultQuestions})

@login_required
def newConcept(request, board_id):
    board = Board.objects.prefetch_related(
        Prefetch('defaultQuestions', to_attr='boardQuestions'),
    ).get(id=board_id)

    allQuestions = list(Question.objects.all().values_list('title', flat=True))
    boardQuestions = [question.title for question in board.boardQuestions]

    if request.method == 'POST':
        form = NewConcept(request.POST)
        if form.is_valid():
            concept = form.save(commit=False)
            concept.board = board
            concept.save()
            concept.questions.set([question.title for question in board.boardQuestions])
            

            return redirect('conceptPage', board_id = board.id, concept_id= concept.id)
    else:
        form = NewConcept()

    return render(request, 'dashboard/newConcept.html', {'board' : board, 'form' : form, 'allQuestions' : allQuestions, 'boardQuestions' : boardQuestions})

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
def loadConceptsCSV(request, board_id):

    allQuestions = Question.objects.all()
    allQuestionTitles = [question.title.strip() for question in allQuestions]
    
    allTags = list(Tag.objects.filter(board_id=board_id))
    allConcepts = list(Concept.objects.filter(board_id=board_id))

    board = Board.objects.prefetch_related(
        Prefetch('defaultQuestions', to_attr='questions')
    ).get(id=board_id)
    existingTags = set(tag.name for tag in allTags)
    existingConcepts = set((concept.answer, concept.definition, concept.hint) for concept in allConcepts)

    if request.method =='POST':
        questionMap = {question.title: question for question in allQuestions}

        if request.POST.get('confirm') == 'true':
            uploadedFile = request.FILES['file']
            fileBytes = uploadedFile.read()
            reader = csv.DictReader(io.StringIO(fileBytes.decode('utf-8')))
            newConcepts = []
            newTagNames = set()

            for row in reader:
                answer = row['Answer']
                definition = row['Definition']
                hint = row['Hint']
                tagsToAdd = set(tag.strip() for tag in row['Tags'].split(',') if tag.strip())
                questionsRaw = row.get('Questions') or ''
                questionsToAdd = [question.strip() for question in questionsRaw.split(',') if question.strip() in allQuestionTitles]
                if not questionsToAdd:
                    questionsToAdd = [] 
                    

                if(answer, definition, hint) not in existingConcepts:
                    existingConcepts.add((answer, definition, hint))
                    newConcepts.append({
                        'answer' : answer,
                        'definition' : definition,
                        'hint' : hint,
                        'tags' : tagsToAdd,
                        'questions' : questionsToAdd
                    })

                for tagName in tagsToAdd:
                    if tagName not in existingTags:
                        newTagNames.add(tagName)
                        existingTags.add(tagName)
            
            tagsToCreate = [Tag(board=board, name=name) for name in newTagNames]
            Tag.objects.bulk_create(tagsToCreate)

            allTags = list(Tag.objects.filter(board=board))
            tagMap = {tag.name: tag for tag in allTags}

            conceptObjects = [
                Concept(
                    board=board,
                    answer=concept['answer'],   
                    definition=concept['definition'],
                    hint=concept['hint']
                ) for concept in newConcepts
            ]
            Concept.objects.bulk_create(conceptObjects)
            

            addTagRelations = []
            for conceptDict, conceptObj in zip(newConcepts, conceptObjects):
                for tagName in conceptDict['tags']:
                    addTagRelations.append(
                        Concept.tags.through(concept_id=conceptObj.id, tag_id=tagMap[tagName].id)
                    )
            Concept.tags.through.objects.bulk_create(addTagRelations)


            addQuestionRelations = []
            for conceptDict, conceptObj in zip(newConcepts, conceptObjects):
                questions = conceptDict.get('questions', [])
                if not questions:
                    questionObject = questionMap.get('answer')
                for questionTitle in questions:
                    questionObject = questionMap.get(questionTitle)
                    if questionObject:
                        addQuestionRelations.append(
                            Concept.questions.through(concept_id=conceptObj.id, question_id=questionTitle)
                        )
            Concept.questions.through.objects.bulk_create(addQuestionRelations) 

            return JsonResponse({'success' : True})
        
        # Branch for counting new concepts and new tags for confirm modal
        if request.POST.get('confirm') == 'false':
            uploadedFile = request.FILES['file']
            fileBytes = uploadedFile.read()
            reader = csv.DictReader(io.StringIO(fileBytes.decode('utf-8')))

            newConceptsCount = 0
            newTagsCount = 0

            if reader:
                #Only Appends New Concepts to Concept Model
                for row in reader:
                    if not any(row):
                        continue

                    answer = row['Answer']
                    definition = row['Definition']
                    hint = row['Hint']
                    tagsToAdd = set(tag.strip() for tag in row['Tags'].split(',') if tag.strip())
                    
                    # Checks if the current question is in the list of existing concepts
                    if (answer, definition, hint) not in existingConcepts:
                        newConceptsCount += 1
                        existingConcepts.add((answer, definition, hint))

                    # Gets all tags from the current row and checks if any are new tags    
                    for tag in tagsToAdd:
                        if tag not in existingTags:
                            newTagsCount += 1
                            existingTags.add(tag)

                return JsonResponse({'success': True, 'newTagsCount': newTagsCount, 'newConceptsCount' : newConceptsCount})

        return JsonResponse({'success' : False})


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
    Concept.objects.filter(board_id=board_id).delete()
    
    return redirect('boardPage', board_id)

@login_required
def deleteAllTags(request, board_id):
    Tag.objects.filter(board_id=board_id).delete()
    
    return redirect('boardPage', board_id)

@login_required
def allQuestionsAPI(request, board_id):
    board = Board.objects.prefetch_related(
        Prefetch('defaultQuestions', to_attr='boardQuestions'),
    ).get(id=board_id)

    allQuestions = list(Question.objects.all().values_list('title', flat=True))
    boardQuestions = [question.title for question in board.boardQuestions]

    if board:
        return JsonResponse({ 'success' : True, 'baseQuestions' : allQuestions, 'boardDefaultQuestions' : boardQuestions})
    return JsonResponse({ 'success' : False})