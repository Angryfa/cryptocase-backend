from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CaseTypeViewSet, CaseViewSet

router = DefaultRouter()
router.register(r"types", CaseTypeViewSet, basename="case-type")
router.register(r"", CaseViewSet, basename="case")

urlpatterns = [ path("", include(router.urls)), ]
