import datetime

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


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
        return self.time_started.time()

    def get_percentage(self):
        try:
            return (self.focus_length / self.session_length) * 100
        except:
            return 0

    def get_focus_length(self):
        image_list = Image.objects.filter(analysis_session=self)
        image_list_focus = image_list.filter(status=True)
        try:
            self.focus_length = (len(image_list_focus) / len(image_list)) * self.session_length
        except ZeroDivisionError:
            self.focus_length = datetime.timedelta(seconds=0)

        return self.focus_length

    def end_session(self):
        self.ongoing = False
        tz_info = self.time_started.tzinfo
        # TODO: fix timezone
        self.session_length = datetime.datetime.now(tz_info) - self.time_started
        self.get_focus_length()


    def __str__(self):
        return self.description


class Image(models.Model):
    analysis_session = models.ForeignKey(Analysis, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="analysis/")
    confidence = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], null=True)
    status = models.BooleanField(null=True )

    def __str__(self):
        return f"{self.analysis_session}_{self.timestamp}"
