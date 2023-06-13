import datetime
import os

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from user.models import User


# Create your models here.
class Analysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time_started = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=200)
    session_length = models.DurationField(null=True)
    focus_length = models.DurationField(null=True)
    ongoing = models.BooleanField(default=True)

    def get_date(self):
        return self.time_started.date()

    def get_time(self):
        return self.time_started.time().replace(microsecond=0)

    def get_percentage(self):
        try:
            return (self.focus_length / self.session_length) * 100
        except:
            return 0

    def get_session_length(self):
        return str(self.session_length).split(".")[0]

    def get_focus_length(self):
        image_list = AnalysisImage.objects.filter(analysis_session=self)
        image_list_focus = image_list.filter(status=True)
        try:
            self.focus_length = (len(image_list_focus) / len(image_list)) * self.session_length
        except:
            self.focus_length = datetime.timedelta(seconds=0)

        return str(self.focus_length).split(".")[0]

    def end_session(self):
        self.ongoing = False
        tz_info = self.time_started.tzinfo

        try:
            self.session_length = datetime.datetime.now(tz_info) - self.time_started
        except:
            self.session_length = datetime.timedelta(seconds=0)
        self.get_focus_length()

    def __str__(self):
        return self.description


def path_and_rename(instance, filename):
    upload_to = 'analysis'
    ext = filename.split('.')[-1]
    username = instance.analysis_session.user.username
    filename = '{}_{}.{}'.format(instance.analysis_session, instance.timestamp, ext)
    return os.path.join(upload_to, username, filename)


class AnalysisImage(models.Model):
    analysis_session = models.ForeignKey(Analysis, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to=path_and_rename)
    confidence = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], null=True)
    status = models.BooleanField(null=True)

    def __str__(self):
        return f"{self.analysis_session}_{self.timestamp}"
