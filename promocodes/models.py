from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User


class Promocode(models.Model):
    TYPE_MULTI = "multi"
    TYPE_SINGLE = "single"
    TYPE_CHOICES = (
        (TYPE_MULTI, "Многоразовый"),
        (TYPE_SINGLE, "Одноразовый"),
    )

    code = models.CharField(max_length=64, unique=True, db_index=True)
    promo_type = models.CharField(max_length=16, choices=TYPE_CHOICES, default=TYPE_MULTI)
    amount_usd = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    # Для многоразовых указываем максимально допустимое число активаций.
    # Для одноразового удобно хранить 1.
    max_activations = models.PositiveIntegerField(default=1)

    # Активен ли промокод и временные ограничения при необходимости
    is_active = models.BooleanField(default=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at", "id")
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"

    def __str__(self) -> str:
        return f"{self.code} ({self.promo_type}) ${self.amount_usd}"

    @property
    def remaining_activations(self) -> int:
        # Количество доступных активаций с учётом уже совершённых
        return max(0, (self.max_activations or 0) - self.activations.count())


class PromocodeActivation(models.Model):
    promocode = models.ForeignKey(Promocode, on_delete=models.CASCADE, related_name="activations")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="promocode_activations")
    amount_usd = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    # Здесь позже можно будет хранить параметры отыгрыша (wager x3),
    # сейчас логику не реализуем — только фиксация факта начисления.
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            ("promocode", "user"),  # чтобы один пользователь не мог активировать один и тот же промокод несколько раз
        )
        ordering = ("-created_at", "id")
        verbose_name = "Активация промокода"
        verbose_name_plural = "Активации промокодов"

    def __str__(self) -> str:
        return f"{self.promocode.code} -> {self.user_id} ${self.amount_usd}"

# Create your models here.
