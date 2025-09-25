from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action


from accounts.serializers import UserWithProfileSerializer
from cases.models import Case, CaseType, Spin
from cases.serializers import CaseDetailSerializer
from referrals.models import ReferralLevelConfig, ReferralProfile
from cashback.models import CashbackSettings
from .serializers_admin import (
    AdminCaseWriteSerializer,
    AdminCaseTypeSerializer,
    AdminReferralLevelSerializer,
    AdminCashbackSettingsSerializer,
)

from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from cashback.services import run_cashback_snapshot

class IsAdmin(permissions.IsAdminUser):
    pass


User = get_user_model()


class AdminUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().select_related("profile").order_by("id")
    serializer_class = UserWithProfileSerializer
    permission_classes = [IsAdmin]

    @action(detail=True, methods=["get"], url_path="details")
    def details(self, request, pk=None):
        user = self.get_object()

        # referrals level 1 and 2
        l1 = ReferralProfile.objects.select_related("user", "referred_by").filter(referred_by=user)
        l2 = ReferralProfile.objects.select_related("user", "referred_by").filter(referred_by__in=l1.values_list("user", flat=True))

        p1 = ReferralLevelConfig.objects.filter(level=1).values_list("percent", flat=True).first()
        p2 = ReferralLevelConfig.objects.filter(level=2).values_list("percent", flat=True).first()
        level1_percent = float(p1) if p1 is not None else 10.0
        level2_percent = float(p2) if p2 is not None else 5.0

        def ser_ref(qs, include_referrer=False, percent=None):
            items = []
            for rp in qs:
                item = {
                    "id": rp.user.id,
                    "email": rp.user.email,
                    "username": rp.user.username,
                    "referred_at": rp.referred_at,
                }
                if include_referrer:
                    rb = rp.referred_by
                    item["referred_by"] = ({"id": rb.id, "email": rb.email, "username": rb.username} if rb else None)
                if percent is not None:
                    item["percent"] = float(percent)
                items.append(item)
            return items

        # spins history
        spins_qs = (
            Spin.objects.filter(user=user)
            .select_related("case", "prize")
            .order_by("-created_at")
        )
        spins = [
            {
                "id": sp.id,
                "created_at": sp.created_at,
                "case": {"id": sp.case_id, "name": sp.case.name},
                "prize": {"id": sp.prize_id, "title": sp.prize.title, "amount_usd": sp.prize.amount_usd},
            }
            for sp in spins_qs
        ]

        return Response({
            "user": self.get_serializer(user).data,
            "referrals": {
                "level1_percent": level1_percent,
                "level2_percent": level2_percent,
                "level1": ser_ref(l1, include_referrer=False, percent=level1_percent),
                "level2": ser_ref(l2, include_referrer=True, percent=level2_percent),
            },
            "spins": spins,
        })


class AdminCaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all().select_related("type").prefetch_related("prizes")
    permission_classes = [IsAdmin]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_serializer_class(self):
        # на запись — write; на чтение — read (с avatar_url)
        if self.action in ("create", "update", "partial_update"):
            return AdminCaseWriteSerializer
        return CaseDetailSerializer

    # Чтобы в ответе на create/update вернуть avatar_url и пр. — сериализуем заново рид-сериализатором:
    def create(self, request, *args, **kwargs):
        w = AdminCaseWriteSerializer(data=request.data, context={"request": request})
        w.is_valid(raise_exception=True)
        instance = w.save()
        r = CaseDetailSerializer(instance, context={"request": request})
        return Response(r.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        w = AdminCaseWriteSerializer(instance, data=request.data, partial=partial, context={"request": request})
        w.is_valid(raise_exception=True)
        instance = w.save()
        r = CaseDetailSerializer(instance, context={"request": request})
        return Response(r.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

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

    @action(detail=False, methods=["post"], url_path="run")
    def run_cashback(self, request):
        """
        POST /api/admin/cashback-settings/run/
        body: { "at": "...", "percent": 10.0, "upsert": true, "dry_run": false }
        """
        data = request.data or {}
        res = run_cashback_snapshot(
            as_of=data.get("at"),
            percent=data.get("percent"),
            upsert=bool(data.get("upsert", True)),
            dry_run=bool(data.get("dry_run", False)),
        )
        if not res.get("ok"):
            return Response({"detail": res.get("error")}, status=status.HTTP_400_BAD_REQUEST)
        return Response(res, status=status.HTTP_200_OK)