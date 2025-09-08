from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

from accounts.serializers import UserWithProfileSerializer
from cases.models import Case, CaseType
from referrals.models import ReferralLevelConfig
from cashback.models import CashbackSettings
from .serializers_admin import AdminCaseWriteSerializer, AdminCaseTypeSerializer, AdminReferralLevelSerializer, AdminCashbackSettingsSerializer


class IsAdmin(permissions.IsAdminUser):
    pass


User = get_user_model()


class AdminUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().select_related("profile").order_by("id")
    serializer_class = UserWithProfileSerializer
    permission_classes = [IsAdmin]


class AdminCaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all().select_related("type").prefetch_related("prizes")
    serializer_class = AdminCaseWriteSerializer
    permission_classes = [IsAdmin]

class AdminCaseTypeViewSet(viewsets.ModelViewSet):
    queryset = CaseType.objects.all()
    serializer_class = AdminCaseTypeSerializer
    permission_classes = [IsAdmin]

class AdminReferralLevelViewSet(viewsets.ModelViewSet):
    queryset = ReferralLevelConfig.objects.all().order_by("level")
    serializer_class = AdminReferralLevelSerializer
    permission_classes = [IsAdmin]

class AdminCashbackSettingsViewSet(viewsets.ModelViewSet):
    queryset = CashbackSettings.objects.all()
    serializer_class = AdminCashbackSettingsSerializer
    permission_classes = [IsAdmin]


