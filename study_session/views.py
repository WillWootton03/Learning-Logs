from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
import json
import uuid
import random

from .models import Session, SessionSettings
from dashboard.models import Board, Tag, Concept


# Create your views here.
@login_required
def newSessionSettings(request, board_id):
    board = Board.objects.get(id=board_id)
    sessionSettings = None
    if request.method == 'POST':
        data = json.loads(request.body)
        sessionSettings = SessionSettings()
        sessionSettings.board =  board
        if 'title' in data:
            sessionSettings.title = data['title']
        
        sessionSettings.save()
        if 'tags' in data:
            tags = Tag.objects.filter(id__in=data['tags'])
            sessionSettings.tags.set(tags)
        
        return JsonResponse({'success' : True, 'board_id' : board.id, 'redirect_url' : reverse('boardPage', args=[board_id])})

    availableTags = list(board.tags.all().values('id','name'))
    return render (request, 'sessions/sessionSettings.html', { 'board': board,  'availableTags' : availableTags })

@login_required
def updateSessionSettings(request, board_id, sessionSettings_id):
    board = Board.objects.get(id=board_id)
    sessionSettings = SessionSettings.objects.get(id=sessionSettings_id)
    if request.method == 'POST':
        data = json.loads(request.body) 
        print(data['isExclusive'])
        if 'title' in data:
            sessionSettings.title = data['title']
        if 'tags' in data:
            tags = Tag.objects.filter(id__in=data['tags'])
            sessionSettings.tags.set(tags)
        if 'isExclusive' in data:
            sessionSettings.isExclusive = data['isExclusive']
        
        sessionSettings.save()

        return JsonResponse({'success' : True, 'board_id' : board.id, 'redirect_url' : reverse('boardPage', args=[board_id])})
    
    sessionSettingsTags = list(sessionSettings.tags.all().values('id','name'))
    availableTags_qs = board.tags.exclude(id__in=sessionSettings.tags.values_list('id', flat=True))
    availableTags = list(availableTags_qs.values('id','name'))
    return render (request, 'sessions/sessionSettings.html', {'board': board, 'sessionSettings' : sessionSettings,  'availableTags' : availableTags, 'sessionSettingsTags' : sessionSettingsTags })

@login_required
@require_POST
def deleteSessionSettings(request, board_id, sessionSettings_id):
    sessionSetings = SessionSettings.objects.get(id=sessionSettings_id)
    sessionSetings.delete()
    return redirect('boardPage', board_id)


@login_required
def sessionSettingsToggleTags(request, board_id, sessionSettings_id, tag_id):
    board = Board.objects.get(id=board_id)
    sessionSettings = SessionSettings.objects.get(id=sessionSettings_id)
    tag = Tag.objects.get(id=tag_id)

    if tag in SessionSettings.tags.all():
        sessionSettings.tags.remove(tag)
    else:
        sessionSettings.tags.add(tag)

    #Updates tag boxes
    sessionSettingsTags = list(SessionSettings.tags.values('id', 'name'))
    availableTags = list(board.tags.exclude(id__in=sessionSettings.tags.all().values_list('id', flat=True)).values('id','name'))

    return JsonResponse({'sessionSettingsTags' : sessionSettingsTags, 'availableTags' : availableTags})


@login_required
def sessionStart(request, board_id, sessionSettings_id):
    board = Board.objects.get(id=board_id)
    sessionSettings = SessionSettings.objects.get(id=sessionSettings_id)
    if request.method == 'POST':
        data = json.loads(request.body)
        availableConcepts = []

        # Converts the input strings from data into actual UUID objects
        tagUuids = {uuid.UUID(t) for t in data['tags']} 

        for concept in board.concepts.all():
            conceptTagIds = set(concept.tags.values_list('id', flat=True))
            if sessionSettings.isExclusive:
                isValid = tagUuids == conceptTagIds
            else:
                isValid = tagUuids.issubset(conceptTagIds)

            if isValid:
                availableConcepts.append(concept)

        print(availableConcepts)
        session = Session.objects.create(board=board)
        session.concepts.set(availableConcepts)

        return JsonResponse({'success' : True, 'redirect_url' : reverse('sessionPage', args=[board_id, session.id])})
    return JsonResponse({'success' : False})

@login_required
def sessionPage(request, board_id, session_id):
    board = Board.objects.get(id=board_id)
    session = Session.objects.get(id=session_id)

    concepts = session.concepts.all()

    if concepts.exists():
        question = random.choice(concepts)

    return render(request, 'sessions/sessionPage.html', {'board' : board, 'session' : session, 'question' : question})

@login_required
@require_POST
def newQuestion(request, board_id, session_id):
    board = Board.objects.get(id=board_id)
    session = Session.objects.get(id=session_id)
    data = json.loads(request.body)
    questionId = uuid.UUID(data.get('questionId'))
    concepts = session.concepts.exclude(id=questionId)
    if concepts.exists():
        question = random.choice(concepts)
    return JsonResponse({'success' : True, 'questionAnswer' : question.answer, 'questionId' : question.id, 'questionHint' : question.hint, 'questionAnswer' : question.answer })

@login_required
@require_POST
def submitAnswer(request, board_id, session_id):
    board = Board.objects.get(id=board_id)
    session = Session.objects.get(id=session_id)
    submitedAnswer = request.POST.get('answer-input', '') 
    submitedAnswer = str(submitedAnswer).strip().lower()
    question_id = request.POST.get('question_id')
    if(question_id):
        try:
            question_id = uuid.UUID(question_id)
            concept = Concept.objects.get(id=question_id)
            if(concept):
                acceptableDefinitions = concept.definition.strip().lower().split('/')
                print(acceptableDefinitions)
                result = (submitedAnswer in acceptableDefinitions)
                if result:
                    session.correctAnswers += 1
                    concept.count += 1
                    if concept.count >= board.knownThreshold:
                        concept.known = True
                    if concept.unknown:
                        concept.unknown = False
                else:
                    session.incorrectAnswers += 1
                    concept.count = 0
                    concept.known = False
                concept.save()
                session.save()
                return JsonResponse({'success' : True, 'result' : result, 'answer' : concept.definition })
        except:
            return JsonResponse({'success' : False})
    return JsonResponse({'success' : False})