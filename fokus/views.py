import json
from datetime import datetime

from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from fokus.models import Analysis
from fokus.serializers import AnalysisSerializer


# Create your views here.
class AnalysisList(APIView):
    def get(self, request, format=None):
        analyses = Analysis.objects.all()
        serializer = AnalysisSerializer(analyses, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        data = request.data
        if data['start'] == 'true':
            analysis = Analysis(user=request.user,
                                time_started=datetime.now(),
                                description=data['description'],
                                ongoing=True,
                                )

            Analysis.save(analysis)

            response = {
                "error": "false",
                "message": "New session successfully created!",
                "description": analysis.description,
                "id": analysis.id,
                "ongoing": analysis.ongoing,
            }

            return Response(response)
        else:
            return Response({"message": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)


class AnalysisDetail(APIView):

    def get(self, request, pk, format=None):
        analysis = get_object_or_404(Analysis.objects.all(), pk=pk)
        serializer = AnalysisSerializer(analysis)

        return Response(serializer.data)

    def put(self, request, pk):
        data = request.data
        analysis = get_object_or_404(Analysis.objects.all(), pk=pk)
        if data['ongoing'] == 'false':
            analysis.end_session()
            Analysis.save(analysis)
            response = {
                "error": False,
                "message": "Session stopped and saved!",
                "id": analysis.id,
                "ongoing": analysis.ongoing,
            }

            return Response(response)
        else:
            # TODO: implement put request with images
            pass
