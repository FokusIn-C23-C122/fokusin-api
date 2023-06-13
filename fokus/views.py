import json
import datetime
from io import BytesIO
from urllib import request

import requests
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import viewsets, permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from fokus.models import Analysis, AnalysisImage
from fokus.serializers import AnalysisSerializer, AnalysisImageSerializer


# Create your views here.
class AnalysisList(APIView):
    def get(self, request, format=None):
        analyses = Analysis.objects.filter(ongoing=False)
        serializer = AnalysisSerializer(analyses, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        data = request.data
        if data['start'] == 'true':
            try:
                current_ongoing = Analysis.objects.get(ongoing=True, user=request.user)
                current_ongoing.end_session()
            except Analysis.DoesNotExist:
                pass
            except Analysis.MultipleObjectsReturned:
                for analysis in Analysis.objects.filter(ongoing=True, user=request.user):
                    analysis.end_session()

            try:
                analysis = Analysis(user=request.user,
                                    time_started=datetime.datetime.now(),
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
            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"message": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        data = request.data
        try:
            analysis = Analysis.objects.get(user=request.user, ongoing=True)
            return AnalysisDetail.as_view()(request._request, pk=analysis.id)
        except Analysis.DoesNotExist:
            return Response({'message': 'No currently ongoing session'}, status=status.HTTP_400_BAD_REQUEST)
        except Analysis.MultipleObjectsReturned:
            analysis_list = Analysis.objects.filter(ongoing=True, user=request.user).order_by('time_started')
            print(analysis_list)
            for analysis in analysis_list[:len(analysis_list) - 1]:
                analysis.end_session()
                analysis.save()
            return self.put(request)


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
                "time_started": analysis.time_started,
                "session_length": str(analysis.session_length).split(".")[0],
                "focus_length": str(analysis.focus_length).split(".")[0]
            }

            return Response(response)
        else:
            try:
                _file = request.data['file']
                image = AnalysisImage(analysis_session=analysis, image=_file)
                AnalysisImage.save(image)

                predict_response = requests.post('https://fokusin-model-ejh5i5qlpq-et.a.run.app/predict',
                                                 json={'image_url': image.image.url})

                confidence = predict_response.json()['predict_image']

                image.status = True if confidence > 0.50 else False
                image.confidence = confidence
                image.save()

                response = {
                    "analysis_id": analysis.id,
                    "focus": image.status,
                    "confidence": image.confidence
                }

                return Response(response)
            except MultiValueDictKeyError:
                return Response({"message": "No image supplied"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
