from decimal import Decimal
from django.db import transaction
from accounts.models import Profile  # у тебя уже есть (balance_usd)
from .models import ReferralProfile, ReferralLevelConfig, ReferralBonus

def _get_percent(level: int) -> Decimal:
    val = (ReferralLevelConfig.objects
           .filter(level=level)
           .values_list("percent", flat=True)
           .first())
    return Decimal(val or 0)

@transaction.atomic
def award_referral_bonuses_for_deposit(deposit):
    """
    Начисляет бонусы L1/L2 за ПОДТВЕРЖДЁННЫЙ депозит и сразу пополняет баланс рефереров.
    Идемпотентно благодаря unique_together(deposit, level).
    Ожидает у депозита поля:
      - deposit.user  -> кто внёс депозит (реферал)
      - deposit.amount_usd (Decimal) -> сумма в USD
    Если у тебя другое имя (например amount), поменяй чтение ниже.
    """
    # ---- входные данные
    referral_user = deposit.user
    amount_usd = Decimal(getattr(deposit, "amount_usd", 0) or 0)  # <-- ПО НУЖДЕ: поменяй имя поля
    if amount_usd <= 0:
        return []

    # ---- цепочка рефералов
    rp = (ReferralProfile.objects
          .select_related("referred_by")
          .filter(user=referral_user)
          .first())
    if not rp or not rp.referred_by_id:
        return []  # нет пригласившего — бонусов нет

    l1_user = rp.referred_by
    l2_user = None
    if l1_user:
        rp2 = (ReferralProfile.objects
               .select_related("referred_by")
               .filter(user=l1_user)
               .first())
        if rp2 and rp2.referred_by_id:
            l2_user = rp2.referred_by

    # ---- проценты уровней
    p1 = _get_percent(1)
    p2 = _get_percent(2)

    to_pay = []
    if l1_user and p1 > 0:
        to_pay.append((1, l1_user, p1))
    if l2_user and p2 > 0:
        to_pay.append((2, l2_user, p2))

    if not to_pay:
        return []

    # ---- залочим профили для корректного инкремента баланса
    user_ids = [u.id for _, u, _ in to_pay]
    profiles = {p.user_id: p for p in Profile.objects.select_for_update().filter(user_id__in=user_ids)}

    results = []
    for level, referrer, percent in to_pay:
        bonus = (amount_usd * percent / Decimal("100")).quantize(Decimal("0.01"))
        if bonus <= 0:
            continue

        # создаём запись; если уже была — пропускаем начисление (идемпотентность)
        obj, created = ReferralBonus.objects.get_or_create(
            deposit=deposit,
            level=level,
            defaults={
                "referrer": referrer,
                "referral": referral_user,
                "percent": percent,
                "amount_usd": bonus,
            },
        )
        if created:
            prof = profiles.get(referrer.id)
            if not prof:
                prof, _ = Profile.objects.get_or_create(user=referrer)
            prof.balance_usd = (prof.balance_usd or Decimal("0")) + bonus
            prof.save(update_fields=["balance_usd", "updated_at"])
        results.append(obj)
    return results
