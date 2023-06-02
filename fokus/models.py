import datetime

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


# Create your models here.
class Analysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time_started = models.DateTimeField(default=datetime.datetime.now())
    description = models.CharField(max_length=200)
    session_length = models.DurationField(null=True)
    focus_length = models.DurationField(null=True)
    ongoing = models.BooleanField(default=True)

    def get_date(self):
        return self.time_started.date()

    def get_time(self):
        return self.time_started.time()

    def get_percentage(self):
        try:
            return (self.focus_length / self.session_length) * 100
        except:
            return 0

    def end_session(self):
        self.ongoing = False
        tz_info = self.time_started.tzinfo
        # TODO: fix timezone
        self.session_length = datetime.datetime.now(tz_info) - self.time_started
    def __str__(self):
        return self.description


class Image(models.Model):
    analysis_session = models.ForeignKey(Analysis, on_delete=models.CASCADE)
    timestamp = models.DurationField(default=datetime.datetime.now())
    image = models.ImageField(upload_to="analysis/")
    confidence = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    status = models.BooleanField()

    def __str__(self):
        return f"{self.analysis_session}_{self.timestamp}"
