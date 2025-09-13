# cashback/services.py
from decimal import Decimal
from django.db.models import Sum
from django.utils import timezone

from cashback.models import CashbackSettings, CashbackAccrual
from accounts.models import Deposit, DepositStatus, Withdrawal, WithdrawalStatus
from django.contrib.auth import get_user_model

User = get_user_model()

def _parse_iso_as_aware(s: str):
    try:
        dt = timezone.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_current_timezone())
        return dt
    except Exception:
        return None

def run_cashback_snapshot(as_of=None, percent=None, upsert=False, dry_run=False):
    """
    Рассчитать кэшбэк на момент as_of (datetime | ISO | None=now) с заданным процентом (Decimal|str|None).
    Возврат: dict с итогами.
    """
    settings = CashbackSettings.objects.first()
    if not settings or not settings.enabled:
        return {"ok": False, "error": "Cashback disabled or not configured."}

    # момент времени
    if as_of:
        if isinstance(as_of, str):
            as_of_dt = _parse_iso_as_aware(as_of)
            if not as_of_dt:
                return {"ok": False, "error": "Bad --at format, use ISO 8601"}
        else:
            as_of_dt = as_of
    else:
        as_of_dt = timezone.now()

    # процент
    try:
        pct = Decimal(percent) if percent is not None else settings.percent
    except Exception:
        return {"ok": False, "error": "Bad percent value"}

    dep_ok = DepositStatus.objects.filter(code="approved").first()
    wdr_ok = WithdrawalStatus.objects.filter(code="approved").first()
    if not dep_ok or not wdr_ok:
        return {"ok": False, "error": "Need DepositStatus/WithdrawalStatus(code='approved')"}

    dep_status_id = dep_ok.id
    wdr_status_id = wdr_ok.id

    created = updated = skipped = 0

    for u in User.objects.all().iterator():
        dep_sum = (Deposit.objects
                   .filter(user=u, status_id=dep_status_id, processed_at__lte=as_of_dt)
                   .aggregate(s=Sum("amount_usd"))["s"] or Decimal("0.00"))
        wdr_sum = (Withdrawal.objects
                   .filter(user=u, status_id=wdr_status_id, processed_at__lte=as_of_dt)
                   .aggregate(s=Sum("amount_usd"))["s"] or Decimal("0.00"))

        base_net = dep_sum - wdr_sum
        if base_net <= 0:
            skipped += 1
            continue

        amount = (base_net * pct / Decimal("100")).quantize(Decimal("0.01"))

        existing = CashbackAccrual.objects.filter(user=u, slot_started_at=as_of_dt).first()
        if existing:
            if upsert:
                existing.amount_usd = amount
                existing.base_deposits_usd = dep_sum
                existing.base_withdrawals_usd = wdr_sum
                existing.base_net_usd = base_net
                existing.percent_used = pct
                if not dry_run:
                    existing.save(update_fields=[
                        "amount_usd", "base_deposits_usd", "base_withdrawals_usd",
                        "base_net_usd", "percent_used"
                    ])
                updated += 1
            else:
                skipped += 1
            continue

        if not dry_run:
            CashbackAccrual.objects.create(
                user=u,
                amount_usd=amount,
                base_deposits_usd=dep_sum,
                base_withdrawals_usd=wdr_sum,
                base_net_usd=base_net,
                percent_used=pct,
                slot_started_at=as_of_dt,
                status=CashbackAccrual.STATUS_CALCULATED,
            )
        created += 1

    return {
        "ok": True,
        "as_of": as_of_dt.isoformat(),
        "percent": str(pct),
        "dry_run": bool(dry_run),
        "created": created,
        "updated": updated,
        "skipped": skipped,
    }
