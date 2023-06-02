from django.contrib.auth.models import User
from rest_framework import serializers

from fokus.models import Analysis, Image


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class AnalysisSerializer(serializers.ModelSerializer):
    date = serializers.DateField(source='get_date')
    time = serializers.TimeField(source='get_time')
    focus_percentage = serializers.IntegerField(source='get_percentage')

    class Meta:
        model = Analysis
        fields = ['date', 'time', 'description', 'session_length', 'focus_length', 'focus_percentage']


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'
