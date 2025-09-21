from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .models import ReferralProfile, gen_code, ReferralLevelConfig, ReferralBonus
from .serializers import ReferralBonusSerializer
from django.db.models import Sum

User = get_user_model()

def _get_or_create_ref_profile(user):
    """Гарантированно вернёт ReferralProfile с уникальным code."""
    rp, _ = ReferralProfile.objects.get_or_create(user=user)
    if not rp.code:
        c = gen_code()
        while ReferralProfile.objects.filter(code=c).exists():
            c = gen_code()
        rp.code = c
        rp.save(update_fields=["code"])
    return rp

def _serialize(qs, include_referrer: bool = False, percent: float | None = None, earned_map: dict[int, float] | None = None):
    #Сериализация списка рефералов. При include_referrer=True добавляем 'referred_by'.
    # список рефералов: id, email, username, referred_at
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
            item["referred_by"] = (
                {"id": rb.id, "email": rb.email, "username": rb.username}
                if rb else None
            )
        if percent is not None:
            item["percent"] = float(percent)
        if earned_map is not None:
            item["earned_usd"] = float(earned_map.get(rp.user_id, 0.0))
        items.append(item)
    return items

class MyReferralInfoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        rp = _get_or_create_ref_profile(request.user)

        # добавили 'referred_by' в select_related для экономии запросов
        l1_qs = (
            ReferralProfile.objects
            .select_related("user", "referred_by")
            .filter(referred_by=request.user)
        )
        l2_qs = (
            ReferralProfile.objects
            .select_related("user", "referred_by")
            .filter(referred_by__in=l1_qs.values_list("user", flat=True))
        )

        frontend = getattr(settings, "FRONTEND_BASE_URL", "http://localhost:3000")
        link = f"{frontend}/register?ref={rp.code}"

        # проценты уровней (по умолчанию 10 и 5)
        p1 = (
            ReferralLevelConfig.objects.filter(level=1).values_list("percent", flat=True).first()
        )
        p2 = (
            ReferralLevelConfig.objects.filter(level=2).values_list("percent", flat=True).first()
        )
        level1_percent = float(p1) if p1 is not None else 10.0
        level2_percent = float(p2) if p2 is not None else 5.0
        # ==== заработок по каждому рефералу (L1/L2) ====
        l1_ids = list(l1_qs.values_list("user_id", flat=True))
        l2_ids = list(l2_qs.values_list("user_id", flat=True))
        l1_map={
            row["referral_id"]: float(row["total"] or 0)
            for row in ReferralBonus.objects
            .filter(referrer=request.user, level=1, referral_id__in=l1_ids)
            .values("referral_id")
            .annotate(total=Sum("amount_usd"))
        }
        l2_map={
            row["referral_id"]: float(row["total"] or 0)
            for row in ReferralBonus.objects
            .filter(referrer=request.user, level=2, referral_id__in=l2_ids)
            .values("referral_id")
            .annotate(total=Sum("amount_usd"))
        }
        earned_level1_usd = float(sum(l1_map.values()))
        earned_level2_usd = float(sum(l2_map.values()))
        earned_total_usd = float(earned_level1_usd + earned_level2_usd)

        return Response({
            "code": rp.code,
            "link": link,
            "level1_count": l1_qs.count(),
            "level2_count": l2_qs.count(),
            # можно включить referrer для обоих уровней; важно хотя бы для L2
            "level1": _serialize(l1_qs, include_referrer=False, percent=level1_percent, earned_map=l1_map),
            "level2": _serialize(l2_qs, include_referrer=True,  percent=level2_percent, earned_map=l2_map),

            "level1_percent": level1_percent,
            "level2_percent": level2_percent,
            "earned_level1_usd": earned_level1_usd,
            "earned_level2_usd": earned_level2_usd,
            "earned_total_usd":  earned_total_usd,
        })

class MyReferralBonusesView(APIView):
    """
    GET /api/referrals/bonuses/?page=1&page_size=20&level=1
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = ReferralBonus.objects.filter(referrer=request.user).order_by("-created_at")

        level = request.query_params.get("level")
        if level and str(level).isdigit():
            qs = qs.filter(level=int(level))

        # простая пагинация
        try:
            page = max(1, int(request.query_params.get("page", 1)))
        except ValueError:
            page = 1
        try:
            page_size = min(200, max(1, int(request.query_params.get("page_size", 20))))
        except ValueError:
            page_size = 20

        total = qs.count()
        start = (page - 1) * page_size
        end = start + page_size
        page_qs = qs[start:end]

        data = ReferralBonusSerializer(page_qs, many=True).data
        return Response({
            "count": total,
            "page": page,
            "page_size": page_size,
            "results": data,
        })
