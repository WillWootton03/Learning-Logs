from django.db import models
import uuid
from django.utils import timezone
from dashboard.models import Board


# Create your models here.
class Log(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='logs')
    title = models.CharField(max_length=255)
    content = models.TextField()
