from django.urls import path
from .views import MyReferralInfoView, MyReferralBonusesView

urlpatterns = [
    path("me/", MyReferralInfoView.as_view(), name="referrals-me"),
    path("bonuses/", MyReferralBonusesView.as_view(), name="referrals-bonuses"),
]
