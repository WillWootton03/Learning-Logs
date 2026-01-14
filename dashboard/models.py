from django.db import models
from accounts.models import User
import uuid

# Create your models here.
class Question(models.Model):
    title = models.CharField(max_length=60, primary_key=True)

    @property
    def display_title(self):
        return self.title.replace('_', ' ').title()

class Board(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='boards')
    title = models.CharField(max_length=200)
    description = models.TextField()
    knownThreshold = models.IntegerField(default=5)
    defaultQuestions = models.ManyToManyField(Question, related_name='boards')

    def __str__(self):
        return self.title

class Tag(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tags')
    
    name = models.CharField(max_length=60)


class Concept(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='concepts')
    answer = models.CharField(max_length=200)
    definition = models.TextField()
    hint = models.TextField(default=None)
    known = models.BooleanField(default=False)
    unknown = models.BooleanField(default=True)
    count = models.IntegerField(default=0)
    maxCount = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag, blank=True, related_name='tags')
    questions = models.ManyToManyField(Question, related_name='concepts')

    def __str__(self):
        return self.answer
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.questions.exists():
            defaultQuestions = Question.objects.filter(board=self.board).values_list('title', blank=True)
            self.questions.set(defaultQuestions)
