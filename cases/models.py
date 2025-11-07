from django.db import models
from django.db.models import Q, F, JSONField 
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
import os
import uuid

def upload_to_case(instance, filename: str) -> str:
    # безопасное имя файла: только базовое имя и новый uuid
    base = os.path.basename(filename or "")
    _name, ext = os.path.splitext(base)
    ext = (ext or "").lower()
    new_name = f"{uuid.uuid4().hex}{ext}"
    return f"cases/{instance.id or 'new'}/{new_name}"

def upload_to_prize(instance, filename: str) -> str:
    # безопасное имя файла: только базовое имя и новый uuid
    base = os.path.basename(filename or "")
    _name, ext = os.path.splitext(base)
    ext = (ext or "").lower()
    new_name = f"{uuid.uuid4().hex}{ext}"
    return f"prizes/{instance.id or 'new'}/{new_name}"

class Prize(models.Model):
    """Модель приза с названием и картинкой"""
    name = models.CharField(max_length=255, verbose_name="Название приза")
    image = models.ImageField(
        upload_to=upload_to_prize,
        null=True,
        blank=True,
        verbose_name="Изображение приза"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Приз"
        verbose_name_plural = "Призы"
        ordering = ("name",)

    def __str__(self):
        return self.name

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

    # НОВОЕ: картинка (аватар кейса)
    avatar = models.ImageField(  # <-- было FileField
        upload_to=upload_to_case,
        null=True,
        blank=True,
        verbose_name="Аватар кейса",
    )

    # Бонусная система
    bonus_chance = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        default=Decimal("0.0"),
        verbose_name="Шанс выпадения бонуса (0-1)",
        help_text="Вероятность выпадения бонуса после открытия кейса"
    )
    bonus_type_chance_multiplier = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=Decimal("0.5"),
        verbose_name="Шанс множителя vs доп. открытия (0-1)",
        help_text="Если бонус выпал, вероятность что это будет множитель (иначе - доп. открытие)"
    )
    bonus_multipliers = JSONField(
        null=True,
        blank=True,
        default=list,
        verbose_name="Множители бонуса",
        help_text='Список множителей с весами: [{"multiplier": 2, "weight": 10}, {"multiplier": 3, "weight": 5}]'
    )
    max_bonus_opens = models.PositiveIntegerField(
        default=1,
        verbose_name="Максимум доп. открытий",
        help_text="Максимальное количество дополнительных открытий за один спин"
    )

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
    prize = models.ForeignKey(Prize, on_delete=models.CASCADE, verbose_name="Приз", null=True, blank=True)
    
    # Старые поля для обратной совместимости (будут удалены позже)
    title = models.CharField(max_length=255, null=True, blank=True)
    amount_usd = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    
    # Новые поля для диапазона номинала
    amount_min_usd = models.DecimalField(max_digits=14, decimal_places=2, default=0.01, verbose_name="Минимальная сумма (USD)")
    amount_max_usd = models.DecimalField(max_digits=14, decimal_places=2, default=1.00, verbose_name="Максимальная сумма (USD)")
    
    # Вероятность выпадения (вес)
    weight = models.PositiveIntegerField(default=1, verbose_name="Вес (вероятность)")

    class Meta:
        verbose_name = "Приз кейса"
        verbose_name_plural = "Призы кейса"
        # Убираем unique_together чтобы один приз мог быть в кейсе несколько раз с разными номиналами

    def __str__(self):
        if self.prize:
            return f"{self.prize.name} (${self.amount_min_usd}-${self.amount_max_usd})"
        else:
            return f"{self.title} (${self.amount_usd})"
    
    def get_random_amount(self):
        """Возвращает случайную сумму в диапазоне [amount_min_usd, amount_max_usd]"""
        import random
        from decimal import Decimal
        
        min_amount = float(self.amount_min_usd)
        max_amount = float(self.amount_max_usd)
        
        # Генерируем случайное число в диапазоне
        random_amount = random.uniform(min_amount, max_amount)
        
        # Округляем до 2 знаков после запятой
        return Decimal(str(round(random_amount, 2)))
    
    @property
    def prize_name(self):
        """Для обратной совместимости"""
        return self.prize.name if self.prize else self.title

class Spin(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE)
    case_prize = models.ForeignKey(CasePrize, on_delete=models.PROTECT, verbose_name="Приз кейса", null=True, blank=True)
    user  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    # Старое поле для обратной совместимости
    prize = models.ForeignKey(CasePrize, on_delete=models.PROTECT, null=True, blank=True, related_name="old_spins")

    # Фактическая сумма выигрыша (случайная в диапазоне)
    actual_amount_usd = models.DecimalField(max_digits=14, decimal_places=2, default=0.01, verbose_name="Фактическая сумма выигрыша")
    
    # Бонусная система
    has_bonus = models.BooleanField(default=False, verbose_name="Есть бонус")
    BONUS_TYPE_CHOICES = [
        ('multiplier', 'Множитель'),
        ('extra_open', 'Дополнительное открытие'),
    ]
    bonus_type = models.CharField(
        max_length=20,
        choices=BONUS_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Тип бонуса"
    )
    bonus_multiplier = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Множитель бонуса",
        help_text="Множитель выигрыша (x2, x3 и т.д.)"
    )
    base_amount_usd = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Начальная сумма выигрыша",
        help_text="Сумма выигрыша до применения бонуса"
    )
    bonus_spins = JSONField(
        null=True,
        blank=True,
        verbose_name="Дополнительные спины",
        help_text='Массив дополнительных спинов: [{"spin_id": ..., "amount": ..., "bonus_type": ...}]'
    )

    # NEW: PF-коммит/раскрытие
    server_seed_hash = models.CharField(max_length=64, db_index=True, null=True, blank=True)
    server_seed      = models.TextField(null=True, blank=True)  # можно шифровать на уровне БД/поля
    client_seed      = models.CharField(max_length=64, null=True, blank=True)
    nonce            = models.PositiveIntegerField(default=0, null=True, blank=True)

    roll_digest = models.CharField(max_length=64, null=True, blank=True)  # hex HMAC-SHA256(server_seed, f"{client_seed}:{nonce}")
    rng_value   = models.DecimalField(max_digits=20, decimal_places=18, null=True, blank=True)  # нормированное [0,1)

    # Снимок весов (и, по желанию, курсов призов) на момент спина, чтобы верификация всегда совпадала
    weights_snapshot = JSONField(null=True, blank=True)  # [{"case_prize_id":..., "weight":..., "amount_min_usd":"...", "amount_max_usd":"..."}]

    class Meta:
        verbose_name = "Крутка"
        verbose_name_plural = "Крутки"

    def __str__(self):
        return f"Spin #{self.id} — {self.case.name}: ${self.actual_amount_usd}"
    
    @property
    def prize_info(self):
        """Для обратной совместимости"""
        if self.case_prize:
            return self.case_prize.prize
        elif self.prize:
            return self.prize
        return None


class BonusSpin(models.Model):
    """Дополнительное открытие кейса (бонус)"""
    parent_spin = models.ForeignKey(
        Spin,
        on_delete=models.CASCADE,
        related_name='bonus_spin_records',
        verbose_name="Основной спин",
        help_text="Основной спин, к которому относится это дополнительное открытие"
    )
    case = models.ForeignKey(Case, on_delete=models.CASCADE, verbose_name="Кейс")
    case_prize = models.ForeignKey(CasePrize, on_delete=models.PROTECT, verbose_name="Приз кейса", null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Пользователь")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    # Сумма выигрыша
    actual_amount_usd = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        default=0.01, 
        verbose_name="Сумма выигрыша"
    )
    
    # Provably Fair данные
    server_seed_hash = models.CharField(max_length=64, db_index=True, null=True, blank=True, verbose_name="Server Seed Hash")
    server_seed = models.TextField(null=True, blank=True, verbose_name="Server Seed")
    client_seed = models.CharField(max_length=64, null=True, blank=True, verbose_name="Client Seed")
    nonce = models.PositiveIntegerField(default=0, null=True, blank=True, verbose_name="Nonce")
    roll_digest = models.CharField(max_length=64, null=True, blank=True, verbose_name="Roll Digest")
    rng_value = models.DecimalField(max_digits=20, decimal_places=18, null=True, blank=True, verbose_name="RNG Value")
    weights_snapshot = JSONField(null=True, blank=True, verbose_name="Снимок весов")

    class Meta:
        verbose_name = "Дополнительное открытие"
        verbose_name_plural = "Дополнительные открытия"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['parent_spin', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"BonusSpin #{self.id} — к Spin #{self.parent_spin_id}: ${self.actual_amount_usd}"
