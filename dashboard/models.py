from django.db import models
from accounts.models import User
from multiselectfield import MultiSelectField
import uuid

# Create your models here.
class Board(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='boards')
    title = models.CharField(max_length=200)
    description = models.TextField()
    knownThreshold = models.IntegerField(default=5)

    def __str__(self):
        return self.title

class Tag(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tags')
    
    name = models.CharField(max_length=60)

class Question(models.Model):
    title = models.CharField(max_length=60, primary_key=True)

    @property
    def display_title(self):
        return self.title.replace('_', ' ').title()

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
    tags = models.ManyToManyField(Tag, blank=True, related_name='concepts')
    questions = models.ManyToManyField(Question, related_name='questions')

    def __str__(self):
        return self.answer
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.questions.exists():
            defaultQuestion = Question.objects.get(title='answer')
            self.questions.add(defaultQuestion)
