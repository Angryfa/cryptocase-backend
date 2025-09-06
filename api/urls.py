from django.urls import path, include
from .views import health

urlpatterns = [
    path("health/", health, name="health"),
    path("auth/", include("accounts.urls")),  # все эндпоинты авторизации
    path("cases/", include("cases.urls")),
    path("referrals/", include("referrals.urls")), 
    # сюда же потом добавим остальные API-роуты, например:
]
