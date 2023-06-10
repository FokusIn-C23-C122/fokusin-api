from django.urls import path

from fokus.views import AnalysisList, AnalysisDetail

urlpatterns = [
    path('', AnalysisList.as_view()),
    path('<pk>', AnalysisDetail.as_view())
]