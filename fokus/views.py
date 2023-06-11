import json
import datetime
from io import BytesIO
from urllib import request

import tensorflow as tf
from PIL import Image
from tensorflow import keras
from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
import numpy as np
from fokus.models import Analysis, AnalysisImage
from fokus.serializers import AnalysisSerializer, AnalysisImageSerializer


# Create your views here.
class AnalysisList(APIView):
    def get(self, request, format=None):
        analyses = Analysis.objects.all()
        total_session = datetime.timedelta(hours=0, minutes=0, seconds=0)
        total_focused = datetime.timedelta(hours=0, minutes=0, seconds=0)
        for analysis in analyses:
            total_session += analysis.session_length
            total_focused += analysis.focus_length
        serializer = AnalysisSerializer(analyses, many=True)
        return Response({"total_session": total_session, "total_focused": total_focused, "results": serializer.data})

    def post(self, request, format=None):
        data = request.data
        if data['start'] == 'true':
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
        else:
            return Response({"message": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)


varian_dict = {'Fokus': 0, 'TidakFokus': 1}
model = tf.keras.models.load_model('./fokusin_model.h5')


def predict_image(img_path):
    res = request.urlopen(img_path).read()
    img = Image.open(BytesIO(res)).resize((224, 224))

    img_array = tf.keras.utils.img_to_array(img)
    img_array = img_array / 255.
    img_array = tf.expand_dims(img_array, 0)

    varian_list = list(varian_dict.keys())
    prediction = model(img_array)
    pred_idx = np.round(model.predict(img_array)[0][0]).astype('int')
    pred_varian = varian_list[pred_idx]
    return pred_varian


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
            _file = request.data['file']
            image = AnalysisImage(analysis_session=analysis, image=_file)
            # TODO: send image to model, receive analysis results
            AnalysisImage.save(image)

            # TODO: wrap this with try except
            predict_result = predict_image(image.image.url)

            image.status = True if predict_result == "Fokus" else False
            image.confidence = 100 if image.status else 0
            image.save()

            response = {
                "analysis_id": analysis.id,
                "focus": image.status,
                "confindence": image.confidence
            }

            return Response(response)
