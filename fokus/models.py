import datetime

from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Analysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(default=datetime.datetime.now())
    description = models.CharField(max_length=200)
    session_length = models.DurationField()
    focus_length = models.DurationField()


