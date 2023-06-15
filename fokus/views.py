import json
import datetime
from io import BytesIO
from urllib import request

import requests
from django.utils.datastructures import MultiValueDictKeyError
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from fokus.models import Analysis, AnalysisImage
from fokus.serializers import AnalysisSerializer, AnalysisImageSerializer, PUTImageToSessionRequestSerializer, \
    PUTImageToSessionResponseSerializer, POSTCreateNewSessionRequestSerializer, POSTCreateNewSessionResponseSerializer, \
    StopSessionRequestSerializer, StopSessionResponseSerializer


# Create your views here.
class AnalysisList(APIView):
    @swagger_auto_schema(
        responses={200: AnalysisSerializer(many=True)}
    )
    def get(self, _request, format=None):
        analyses = Analysis.objects.filter(ongoing=False, user=_request.user)
        serializer = AnalysisSerializer(analyses, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=POSTCreateNewSessionRequestSerializer,
        responses={201: POSTCreateNewSessionResponseSerializer(many=False)}
    )
    def post(self, _request, format=None):
        data = _request.data
        if data['start'] == 'true':

            analysis = None

            try:
                analysis = Analysis.objects.get(ongoing=True, user=_request.user)
            except Analysis.DoesNotExist:
                analysis = Analysis(user=_request.user,
                                    time_started=datetime.datetime.now(),
                                    description=data['description'],
                                    ongoing=True,
                                    )

                Analysis.save(analysis)
            except Analysis.MultipleObjectsReturned:
                for analysis in Analysis.objects.filter(ongoing=True, user=_request.user):
                    analysis.end_session()
            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

    @swagger_auto_schema(
        request_body=StopSessionRequestSerializer,
        responses={200: StopSessionResponseSerializer(many=False)},
    )
    def put(self, _request):
        try:
            analysis = Analysis.objects.get(user=_request.user, ongoing=True)
            return AnalysisDetail.as_view()(_request._request, pk=analysis.id)
        except Analysis.DoesNotExist:
            return Response({'message': 'No currently ongoing session'}, status=status.HTTP_400_BAD_REQUEST)
        except Analysis.MultipleObjectsReturned:
            analysis_list = Analysis.objects.filter(ongoing=True, user=_request.user).order_by('time_started')
            print(analysis_list)
            for analysis in analysis_list[:len(analysis_list) - 1]:
                analysis.end_session()
                analysis.save()
            return self.put(_request)


class AnalysisDetail(APIView):
    parser_classes = [MultiPartParser, JSONParser]
    @swagger_auto_schema(
        responses={200: AnalysisSerializer(many=False)},
    )
    def get(self, _request, pk, format=None):
        analysis = get_object_or_404(Analysis.objects.filter(user=_request.user), pk=pk)
        serializer = AnalysisSerializer(analysis)

        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=PUTImageToSessionRequestSerializer,
        responses={200: PUTImageToSessionResponseSerializer(many=False)},
    )
    def put(self, _request, pk):
        data = _request.data
        analysis = get_object_or_404(Analysis.objects.filter(user=_request.user), pk=pk)
        if data['ongoing'] == 'false':
            # TODO: handle if session is already stopped
            analysis.end_session()
            Analysis.save(analysis)
            response = {
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
                # TODO: handle if session is already stopped
                _file = _request.data['file']
                image = AnalysisImage(analysis_session=analysis, image=_file)
                AnalysisImage.save(image)

                predict_response = requests.post('https://fokusin-model-ejh5i5qlpq-et.a.run.app/predict',
                                                 json={'image_url': image.image.url})

                confidence = predict_response.json()['predict_image']

                image.status = True if confidence > 0.50 else False
                image.confidence = confidence * 100
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
