from django.db import models
from django.db.models import Q, F
from django.utils import timezone
from django.conf import settings


class CaseType(models.Model):
    type = models.SlugField(max_length=50, unique=True, db_index=True)  # 'standard', 'limited', ...
    name = models.CharField(max_length=100)                             # «Обычный», «Лимитированный», ...
    is_limited = models.BooleanField(default=False)
    is_timed = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("sort_order", "id")
        verbose_name = "Тип кейса"
        verbose_name_plural = "Типы кейсов"

    def __str__(self):
        return self.name

class CaseQuerySet(models.QuerySet):
    def available_now(self):
        """
        Активные кейсы; если тип помечен как timed — проверяем окно доступности.
        """
        now = timezone.now()
        return self.filter(is_active=True).filter(
            Q(type__is_timed=False) |
            (
                (Q(available_from__isnull=True) | Q(available_from__lte=now)) &
                (Q(available_to__isnull=True)   | Q(available_to__gte=now))
            )
        )

class Case(models.Model):
    name = models.CharField(max_length=255)
    price_usd = models.DecimalField(max_digits=10, decimal_places=2)
    spins_total = models.PositiveIntegerField(default=0)
    spins_used = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    # НОВОЕ: тип кейса
    type = models.ForeignKey(CaseType, on_delete=models.PROTECT, related_name="cases", db_index=True)

    # окно доступности (используется, если type.is_timed=True)
    available_from = models.DateTimeField(null=True, blank=True, db_index=True)
    available_to   = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = CaseQuerySet.as_manager()

    def __str__(self):
        return self.name

    def is_available_now(self) -> bool:
        if not self.is_active:
            return False
        now = timezone.now()
        if self.is_timed_mode():
            if self.available_from and now < self.available_from:
                return False
            if self.available_to and now > self.available_to:
                return False
        return True

    @property
    def spins_remaining(self) -> int:
        return max(0, (self.spins_total or 0) - (self.spins_used or 0))

    def is_limited_mode(self) -> bool:
        return bool(self.type and self.type.is_limited)

    def is_timed_mode(self) -> bool:
        return bool(self.type and self.type.is_timed)

class CasePrize(models.Model):
    case = models.ForeignKey(Case, related_name="prizes", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    amount_usd = models.DecimalField(max_digits=14, decimal_places=2)
    weight = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Приз кейса"
        verbose_name_plural = "Призы кейса"

    def __str__(self):
        return f"{self.title} (${self.amount_usd})"

class Spin(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE)
    prize = models.ForeignKey(CasePrize, on_delete=models.PROTECT)
    user  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Крутка"
        verbose_name_plural = "Крутки"

    def __str__(self):
        return f"Spin #{self.id} — {self.case.name}: ${self.prize.amount_usd}"
