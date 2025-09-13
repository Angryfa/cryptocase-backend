from django.urls import path
from .views import MyCashbackListView, MyCashbackSummaryView, MyCashbackClaimView

urlpatterns = [
    path("me/", MyCashbackListView.as_view()),
    path("me/summary/", MyCashbackSummaryView.as_view()),
    path("me/claim/", MyCashbackClaimView.as_view()),
]
