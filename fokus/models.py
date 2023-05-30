import datetime

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


# Create your models here.
class Analysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time_started = models.DateTimeField(default=datetime.datetime.now())
    description = models.CharField(max_length=200)
    session_length = models.DurationField()
    focus_length = models.DurationField()


class Image(models.Model):
    analysis_session = models.ForeignKey(Analysis, on_delete=models.CASCADE)
    timestamp = models.DurationField(default=datetime.datetime.now())
    image = models.ImageField(upload_to="analysis/")
    confidence = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    status = models.BooleanField()

    def __str__(self):
        return f"{self.analysis_session}_{self.timestamp}"

