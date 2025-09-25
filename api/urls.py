from django.urls import path, include
from .views import health
from rest_framework.routers import DefaultRouter
from .views_admin import AdminUserViewSet, AdminCaseViewSet, AdminCaseTypeViewSet, AdminReferralLevelViewSet, AdminCashbackSettingsViewSet

from .views_admin_dashboard import AdminDashboardView

router = DefaultRouter()
router.register(r"users", AdminUserViewSet, basename="admin-users")
router.register(r"cases", AdminCaseViewSet, basename="admin-cases")
router.register(r"case-types", AdminCaseTypeViewSet, basename="admin-case-types")
router.register(r"ref-levels", AdminReferralLevelViewSet, basename="admin-ref-levels")
router.register(r"cashback-settings", AdminCashbackSettingsViewSet, basename="admin-cashback-settings")

urlpatterns = [
    path("health/", health, name="health"),
    path("auth/", include("accounts.urls")),  # все эндпоинты авторизации
    path("cases/", include("cases.urls")),
    path("referrals/", include("referrals.urls")),
    path("support/", include("support.urls")),
    path("admin/dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("admin/", include((router.urls, "admin"), namespace="admin")),
    path("cashback/", include("cashback.urls")),
]
