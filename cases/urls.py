from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CaseTypeViewSet, CaseViewSet, SpinViewSet  # добавляем SpinViewSet

router = DefaultRouter()
router.register(r"types", CaseTypeViewSet, basename="case-type")
router.register(r"", CaseViewSet, basename="case")   # лучше явно "cases", а не пусто
router.register(r"spins", SpinViewSet, basename="spin")   # новый эндпоинт для проверки спинов

urlpatterns = [
    path("", include(router.urls)),
]
