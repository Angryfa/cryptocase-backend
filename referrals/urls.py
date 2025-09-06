from django.urls import path
from .views import MyReferralInfoView

urlpatterns = [
    path("me/", MyReferralInfoView.as_view(), name="referrals-me"),
]
