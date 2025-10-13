from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PrizeViewSet, CaseTypeViewSet, CaseViewSet, SpinViewSet

router = DefaultRouter()
router.register(r"prizes", PrizeViewSet, basename="prize")
router.register(r"types", CaseTypeViewSet, basename="case-type")
router.register(r"", CaseViewSet, basename="case")
router.register(r"spins", SpinViewSet, basename="spin")

urlpatterns = [
    path("", include(router.urls)),
]
