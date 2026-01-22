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
from django.core.cache import cache

from .models import Session, SessionSettings
from dashboard.models import Board, Tag, Concept, Question
from accounts.models import User

# Create your views here.
@login_required
def newSessionSettings(request, board_id):
    board = Board.objects.get(id=board_id)
    
    if request.user == board.user:
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
        return render (request, 'sessions/sessionSettings.html', { 'board': board,  'availableTags' : availableTags,  'options' : questionOptions, 'defaultQuestionList' : defaultQuestions, 'sessionQuestions' : sessionQuestions})
    return redirect('dashboard')

@login_required
def updateSessionSettings(request, board_id, sessionSettings_id = None):
    board = Board.objects.get(id=board_id)
    if request.user == board.user:
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

            return JsonResponse({'success' : True, 'board_id' : board.id, 'sessionSettingsId' : str(sessionSettings.id)})
        
        sessionSettingsTags = list(sessionSettings.tags.all().values('id','name'))
        availableTags_qs = board.tags.exclude(id__in=sessionSettings.tags.values_list('id', flat=True))
        availableTags = list(availableTags_qs.values('id','name'))
        
        questions = [question.title for question in sessionSettings.questionTypes.all()]

        defaultQuestions = [question.title for question in Question.objects.all()]

        return render (request, 'sessions/sessionSettings.html', {'board': board, 'sessionSettings' : sessionSettings,  'availableTags' : availableTags, 'sessionSettingsTags' : sessionSettingsTags, 'defaultQuestionList' : defaultQuestions, 'sessionQuestions' : questions})
    return redirect('dashboard')

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

    return JsonResponse({'sessionSettingsTags' : sessionSettings.sessionSettingsTags, 'availableTags' : board.availableTags})


@login_required
def sessionStart(request, board_id, sessionSettings_id=None):
    board = Board.objects.get(id=board_id)
    if request.user == board.user:
        if request.method == 'POST':
            data = json.loads(request.body)
            tagUuids = list({uuid.UUID(t) for t in data['tags']})
                
            tagCount = len(tagUuids)

            if 'questions' in data:
                questionTypes = Question.objects.filter(title__in=data.get('questions'))

            if tagUuids:
                if data.get('isExclusive'):
                    tagConceptQS = Concept.objects.annotate(
                        matchedTags= Count('tags', filter=Q(tags__id__in=tagUuids), distinct=True),
                        totalTags= Count('tags', distinct=True)
                        ).filter(matchedTags=tagCount, totalTags=tagCount)
                else:
                    tagConceptQS = Concept.objects.annotate(matchedTags=Count('tags', filter=Q(tags__id__in=tagUuids), distinct=True)).filter(matchedTags=tagCount)
            else:
                tagConceptQS = Concept.objects.filter(board=board)


            conceptQS = tagConceptQS.filter(Q(questions__in=questionTypes) | Q(questions__isnull=True)).distinct()

            board = Board.objects.prefetch_related(
                Prefetch('concepts', queryset=conceptQS, to_attr='filteredConcepts') 
            ).get(id=board_id)


            if board.filteredConcepts:
                session = Session.objects.create(board=board)
                session.concepts.set(board.filteredConcepts)
                session.questionTypes.set(questionTypes)

            tagConcepts = list(tagConceptQS.values_list('answer', flat=True).distinct())
            cacheKey = f'board:{board_id}:tagConcepts'
            cache.set(cacheKey, tagConcepts, timeout=600)
            if not tagConcepts:
                return JsonResponse({'success' : False, 'redirect_url' : reverse('boardPage', args=[board_id])})


            return JsonResponse({'success' : True, 'redirect_url' : reverse('sessionPage', args=[board_id, session.id]) })
        return JsonResponse({'success' : False})
    return redirect('dashboard')

@login_required
def sessionPage(request, board_id, session_id):
    board = Board.objects.prefetch_related('defaultQuestions').get(id=board_id)
    if request.user == board.user:
        boardDefaultQuestions = board.defaultQuestions.all()

        # Prefetches the list of questions into a workable list for js
        questionsPrefetch = Prefetch('questions', queryset=Question.objects.only('title'), to_attr='prefetchedQuestions')

        session = Session.objects.prefetch_related(
            Prefetch('concepts', queryset=Concept.objects.prefetch_related(questionsPrefetch),  to_attr='sessionConcepts'),
            Prefetch('questionTypes', queryset=Question.objects.only('title'), to_attr='availableQuestions'),
        ).get(id=session_id)

        questions = {}
        
        for concept in getattr(session, 'sessionConcepts', []):
            questionsList = concept.prefetchedQuestions if concept.prefetchedQuestions else boardDefaultQuestions
            questions[str(concept.id)] = {'answer' : concept.answer, 'definition' : concept.definition, 'hint' : concept.hint, 'count' : concept.count, 'known' : concept.known, 'unknown' : concept.unknown, 'questionTypes' : [type.title for type in questionsList] }
        
        if not questions:
            redirect('boardPage', board.id)
        
        questionTitles = [question.title for question in session.availableQuestions]

        # Checks to see if there is a recent session start instance, if there is will load all tagConcepts from there if not will return to boardPage
        tagConcepts = cache.get(f'board:{board_id}:tagConcepts')
        if tagConcepts is None:
            return redirect('boardPage', board_id)
        

        return render(request, 'sessions/sessionPage.html', {'board' : board, 'session' : session, 'questions' : questions, 'questionTypes' : questionTitles, 'tagConcepts' : tagConcepts, 'defaultBoardQuestions' : list(boardDefaultQuestions.values_list('title', flat=True)) })
    return redirect('dashboard')

@login_required
@csrf_exempt
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

        session = Session.objects.get(id=session_id)
        session.correctAnswers = data['correctAnswers']
        session.incorrectAnswers = data['incorrectAnswers']
        session.save()

    
        return JsonResponse({'success' : True, 'redirect_url': reverse('boardPage', args=[board_id])})
    return JsonResponse({'success' : False})
