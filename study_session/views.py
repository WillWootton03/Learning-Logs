from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Prefetch
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import F, Count, Q
import json, urllib
import uuid
import random

from .models import Session, SessionSettings
from dashboard.models import Board, Tag, Concept, Question


# Create your views here.
@login_required
def newSessionSettings(request, board_id):
    board = Board.objects.get(id=board_id)
    if request.method == 'POST':
        data = json.loads(request.body)
        sessionSettings = SessionSettings()
        sessionSettings.board =  board
        if 'title' in data:
            sessionSettings.title = data['title']
        
        if 'isExclusive' in data:
            sessionSettings.isExclusive = data['isExclusive']

        sessionSettings.save()

        if 'tags' in data:
            tags = Tag.objects.filter(id__in=data['tags'])
            sessionSettings.tags.set(tags)

        if 'questions' in data:
            questions = Question.objects.filter(title__in=data.get('questions'))
            sessionSettings.questionTypes.set(questions)
        
        return JsonResponse({'success' : True, 'board_id' : board.id, 'redirect_url' : reverse('boardPage', args=[board_id])})

    availableTags = list(board.tags.all().values('id','name'))
    questionOptions = list(Question.objects.all().values('title'))
    for option in questionOptions:
        option['formattedTitle'] = option['title'].replace('_', ' ').title()
    defaultQuestions = Question.objects.all()
    defaultQuestions = [question.title for question in defaultQuestions]
    sessionQuestions = ['answer']
    return render (request, 'sessions/sessionSettings.html', { 'board': board,  'availableTags' : availableTags,  'options' : questionOptions, 'defaultQuestions' : defaultQuestions, 'sessionQuestions' : sessionQuestions})

@login_required
def updateSessionSettings(request, board_id, sessionSettings_id = None):
    board = Board.objects.get(id=board_id)
    sessionSettings = SessionSettings.objects.get(id=sessionSettings_id)
    if request.method == 'POST':
        data = json.loads(request.body) 

        if 'title' in data:
            sessionSettings.title = data['title']
        if 'isExclusive' in data:
            sessionSettings.isExclusive = data['isExclusive']

        sessionSettings.save()

        if 'tags' in data:
            tags = Tag.objects.filter(id__in=data['tags'])
            sessionSettings.tags.set(tags)
        if 'questions' in data:
            questions = Question.objects.filter(title__in=data.get('questions'))
            sessionSettings.questionTypes.set(questions)

        return JsonResponse({'success' : True, 'board_id' : board.id, 'redirect_url' : reverse('boardPage', args=[board_id])})
    
    sessionSettingsTags = list(sessionSettings.tags.all().values('id','name'))
    availableTags_qs = board.tags.exclude(id__in=sessionSettings.tags.values_list('id', flat=True))
    availableTags = list(availableTags_qs.values('id','name'))
    questionOptions = list(Question.objects.all().values('title'))
    questions = [question.title for question in sessionSettings.questionTypes.all()]

    defaultQuestions = Question.objects.all()
    defaultQuestions = [question.title for question in defaultQuestions]

    return render (request, 'sessions/sessionSettings.html', {'board': board, 'sessionSettings' : sessionSettings,  'availableTags' : availableTags, 'sessionSettingsTags' : sessionSettingsTags, 'defaultQuestions' : defaultQuestions, 'sessionQuestions' : questions})

@login_required
@require_POST
def deleteSessionSettings(request, board_id, sessionSettings_id):
    sessionSetings = SessionSettings.objects.get(id=sessionSettings_id)
    sessionSetings.delete()
    return redirect('boardPage', board_id)


@login_required
def sessionSettingsToggleTags(request, board_id, sessionSettings_id, tag_id):
    sessionSettings = SessionSettings.objects.prefetch_related(
        Prefetch('tags', list(SessionSettings.tags.values('id', 'name')))
    ).get(id=sessionSettings_id)

    board = Board.objects.prefetch_related(
        Prefetch('availableTags', queryset=list(Tag.objects.filter(board_id=board_id).exclude(id__in=sessionSettings.sessionSettingsTags.all().values_list('id', flat=True)).values('id', 'name')))
    ).get(id=board_id)
    
    tag = Tag.objects.get(id=tag_id)

    if tag in sessionSettings.tags:
        sessionSettings.tags.remove(tag)
    else:
        sessionSettings.tags.add(tag)

    #Updates tag boxes
    # sessionSettingsTags = list(SessionSettings.tags.values('id', 'name'))
    # availableTags = list(board.tags.exclude(id__in=sessionSettings.tags.all().values_list('id', flat=True)).values('id','name'))

    return JsonResponse({'sessionSettingsTags' : sessionSettings.sessionSettingsTags, 'availableTags' : board.availableTags})


@login_required
def sessionStart(request, board_id, sessionSettings_id):
    sessionSettings = SessionSettings.objects.get(id=sessionSettings_id)

    if request.method == 'POST':
        data = json.loads(request.body)
        tagUuids = list({uuid.UUID(t) for t in data['tags']})
        tagCount = len(tagUuids)

        if 'questions' in data:
            questionTypes = Question.objects.filter(title__in=data.get('questions'))

        if sessionSettings.isExclusive:
            conceptQS = Concept.objects.annotate(matchedTags= Count('tags', filter=Q(tags__id__in=tagUuids), distinct=True)).filter(matchedTags=tagCount)
            conceptQS = conceptQS.filter(questions__in=questionTypes).distinct()

            board = Board.objects.prefetch_related(
                Prefetch('concepts', queryset=conceptQS.prefetch_related('questions'), to_attr='filteredConcepts')).get(id=board_id)
        else:
            conceptQS = Concept.objects.annotate(matchedTags=Count('tags', filter=Q(tags__id__in=tagUuids), distinct=True)).filter(matchedTags=tagCount)
            conceptQS = conceptQS.filter(questions__in=questionTypes)
            
            board = Board.objects.prefetch_related(
                Prefetch('concepts', queryset=conceptQS.prefetch_related('questions'), to_attr='filteredConcepts') 
            ).get(id=board_id)

        # Converts the input strings from data into actual UUID objects
        session = Session.objects.create(board=board)
        session.concepts.set(board.filteredConcepts)
        session.questionTypes.set(questionTypes)

        return JsonResponse({'success' : True, 'redirect_url' : reverse('sessionPage', args=[board_id, session.id])})
    return JsonResponse({'success' : False})

@login_required
def sessionPage(request, board_id, session_id):
    board = Board.objects.get(id=board_id)

    # Prefetches the list of questions into a workable list for js
    questionsPrefetch = Prefetch('questions', queryset=Question.objects.only('title'), to_attr='prefetchedQuestions')

    session = Session.objects.prefetch_related(
        Prefetch('concepts', queryset=Concept.objects.prefetch_related(questionsPrefetch),  to_attr='sessionConcepts'),
        Prefetch('questionTypes', queryset=Question.objects.only('title'), to_attr='availableQuestions')
    ).get(id=session_id)

    questions = {}

    questionTitles = [question.title for question in session.availableQuestions]

    if session.sessionConcepts:
        for concept in session.sessionConcepts:
            questions[str(concept.id)] = {'answer' : concept.answer, 'definition' : concept.definition, 'hint' : concept.hint, 'count' : concept.count, 'known' : concept.known, 'unknown' : concept.unknown, 'questionTypes' : [type.title for type in concept.prefetchedQuestions] }
    else:
        #return redirect('boardPage', board_id)
        pass
    
    questions =  json.dumps(questions)

    return render(request, 'sessions/sessionPage.html', {'board' : board, 'session' : session, 'questions' : questions, 'questionTypes' : questionTitles })

@login_required
@require_POST
def submitSession(request, board_id, session_id):
    if request.body:
        data = json.loads(request.body)
        submittedQuestions = {uuid.UUID(k): v for k, v in data.get('questions').items()}

        questionIds = list(submittedQuestions.keys())
        questions = list(Concept.objects.filter(id__in=questionIds))

        for concept in questions:
            questionData = submittedQuestions[concept.id]
            for field, value in questionData.items():
                setattr(concept, field, value)

        Concept.objects.bulk_update(questions, ['count', 'known', 'unknown'])        

        Session.objects.filter(id=session_id).update(
            correctAnswers=data.get('correctAnswers'),
            incorrectAnswers=data.get('incorrectAnswers')
        )
    
        return JsonResponse({'success' : True, 'redirect_url': reverse('boardPage', args=[board_id])})
    return JsonResponse({'success' : False})
""" 
@login_required
@require_POST
def newQuestion(request, board_id, session_id):
    data = json.loads(request.body)
    questionId = uuid.UUID(data.get('questionId'))
    session = Session.objects.prefetch_related(
        Prefetch('concepts', queryset=Concept.objects.exclude(id=questionId), to_attr='sessionConcepts')
    ).get(id=session_id)

    if session.sessionConcepts:
        question = random.choice(session.sessionConcepts)
    else:
        return JsonResponse({'success': False})

    return JsonResponse({'success' : True, 'questionAnswer' : question.answer, 'questionId' : question.id, 'questionHint' : question.hint })

@login_required
@require_POST
def submitAnswer(request, board_id, session_id):

    submitedAnswer = str(request.POST.get('answer-input', '')).strip().lower()
    question_id = request.POST.get('question_id')

    board = Board.objects.only('knownThreshold').get(id=board_id)
    session = Session.objects.get(id=session_id)

    try:
        question_id = uuid.UUID(question_id)
        concept = Concept.objects.get(id=question_id)
    except:
        return JsonResponse({'success' : False})
    
    acceptableDefinitons = [definition.strip().lower() for definition in concept.definition.strip().lower().split('/')]
    result = submitedAnswer in acceptableDefinitons
    
    if result:
        concept.count += 1
        concept.known = concept.count >= board.knownThreshold
        concept.unknown = False
        concept.save(update_fields=['count', 'known', 'unknown'])
        session.correctAnswers += 1
        session.save(update_fields=['correctAnswers'])
    else:
        concept.count = 0
        concept.save(update_fields=['count'])
        session.incorrectAnswers += 1
        session.save(update_fields=['incorrectAnswers'])


    return JsonResponse({'success' : True, 'result' : result, 'answer' : concept.definition })
    """