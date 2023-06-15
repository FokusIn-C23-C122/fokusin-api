import datetime

from django.contrib.auth.models import User
from django.utils.duration import duration_string
from rest_framework import serializers

from fokus.models import Analysis, AnalysisImage


class DurationFieldNoMicrosecond(serializers.DurationField):
    def to_representation(self, value):
        if not value:
            value = datetime.timedelta(seconds=0)

        return value.seconds


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class AnalysisSerializer(serializers.ModelSerializer):
    date = serializers.DateField(source='get_date')
    time = serializers.TimeField(source='get_time')
    focus_percentage = serializers.IntegerField(source='get_percentage')
    session_length = DurationFieldNoMicrosecond()
    focus_length = DurationFieldNoMicrosecond()

    class Meta:
        model = Analysis
        fields = ['date', 'time', 'description', 'session_length', 'focus_length', 'focus_percentage']


class AnalysisImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisImage
        fields = '__all__'


class PUTImageToSessionRequestSerializer(serializers.Serializer):
    ongoing = "true"
    file = serializers.ImageField()


class StopSessionRequestSerializer(serializers.Serializer):
    ongoing = "false"


class StopSessionResponseSerializer(serializers.Serializer):
    message = "Session stopped and saved!"
    id = serializers.IntegerField()
    ongoing = False
    time_started = serializers.DateTimeField()
    session_length = serializers.StringRelatedField()
    focus_length = serializers.StringRelatedField()


class PUTImageToSessionResponseSerializer(serializers.Serializer):
    analysis_id = serializers.IntegerField()
    focus = serializers.BooleanField()
    confidence = serializers.FloatField()


class POSTCreateNewSessionRequestSerializer(serializers.Serializer):
    start = serializers.CharField()
    description = serializers.CharField()


class POSTCreateNewSessionResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    description = serializers.CharField()
    id = serializers.IntegerField()
    ongoing = serializers.CharField()
