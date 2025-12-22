from django.db import models
import uuid

from dashboard.models import Board, Concept


# Create your models here.
class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    concepts = models.ManyToManyField(Concept, blank=True)
    start = models.DateTimeField(auto_now_add=True)