from django.urls import path
from .views import MyCashbackListView

urlpatterns = [ path("me/", MyCashbackListView.as_view()) ]