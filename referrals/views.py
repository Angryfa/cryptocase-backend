from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .models import ReferralProfile, gen_code, ReferralLevelConfig

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

def _serialize(qs, include_referrer: bool = False, percent: float | None = None):
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

        return Response({
            "code": rp.code,
            "link": link,
            "level1_count": l1_qs.count(),
            "level2_count": l2_qs.count(),
            # можно включить referrer для обоих уровней; важно хотя бы для L2
            "level1": _serialize(l1_qs, include_referrer=False, percent=level1_percent),
            "level2": _serialize(l2_qs, include_referrer=True, percent=level2_percent),
            "level1_percent": level1_percent,
            "level2_percent": level2_percent,
        })
