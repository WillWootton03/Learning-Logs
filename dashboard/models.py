from django.db import models
from authentication.models import User
import uuid

# Create your models here.
class Board(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    unknownThreshold = models.IntegerField()
    knownThreshold = models.IntegerField()

    def __str__(self):
        return self.title

class Concept(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    answer = models.CharField(max_length=200)
    definition = models.TextField()
    hint = models.TextField(default=None)
    known = models.BooleanField(default=False)
    unknown = models.BooleanField(default=False)
    count = models.IntegerField(default=0)
    maxCount = models.IntegerField(default=0)

    def __str__(self):
        return self.answer
