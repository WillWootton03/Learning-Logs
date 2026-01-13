from django.db import models
import uuid

from dashboard.models import Board, Concept, Tag, Question


# Create your models here.
class SessionSettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='sessionSettings')
    tags = models.ManyToManyField(Tag, blank=True, related_name='sessions')
    isExclusive = models.BooleanField(default=False)
    questionTypes = models.ManyToManyField(Question, related_name='sessionSettings')
    numQuestions = models.IntegerField(default=0)
    dateAdded = models.DateTimeField(auto_now_add=True)

class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='sessions')
    concepts = models.ManyToManyField(Concept, blank=True, related_name='sessions')
    questionTypes = models.ManyToManyField(Question, related_name='sessions')
    correctAnswers = models.IntegerField(default=0)
    incorrectAnswers = models.IntegerField(default=0)
    dateAdded = models.DateTimeField(auto_now_add=True)
