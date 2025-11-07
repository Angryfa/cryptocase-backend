from django.contrib.auth import get_user_model
from django.db import models, connection
from rest_framework import viewsets, permissions, status, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import action


from accounts.serializers import UserWithProfileSerializer, AdminUserEditSerializer
from accounts.models import Deposit, Withdrawal, DepositStatus, WithdrawalStatus, WithdrawalBlock, DepositBlock, AccountBlock
from cases.models import Case, CaseType, Spin
from cases.serializers import CaseDetailSerializer
from referrals.models import ReferralLevelConfig, ReferralProfile
from cashback.models import CashbackSettings
from .serializers_admin import (
    AdminCaseWriteSerializer,
    AdminCaseTypeSerializer,
    AdminReferralLevelSerializer,
    AdminCashbackSettingsSerializer,
    WithdrawalBlockSerializer,
    DepositBlockSerializer,
    AccountBlockSerializer,
    WithdrawalBlockCreateSerializer,
    DepositBlockCreateSerializer,
    AccountBlockCreateSerializer,
    AdminPromocodeSerializer,
    AdminPromocodeWriteSerializer,
    AdminPromocodeActivationSerializer,
)

from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from cashback.services import run_cashback_snapshot
from promocodes.models import Promocode, PromocodeActivation

class IsAdmin(permissions.IsAdminUser):
    pass


User = get_user_model()


class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().select_related("profile").order_by("id")
    permission_classes = [IsAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ['id', 'email']
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return AdminUserEditSerializer
        return UserWithProfileSerializer

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

        # spins history (первые 20 записей для предварительного просмотра)
        # Показываем все крутки (дополнительные открытия теперь в отдельной таблице BonusSpin)
        spins_qs = (
            Spin.objects.filter(user=user)
            .select_related("case", "prize", "case_prize", "case_prize__prize")
            .prefetch_related("bonus_spin_records")
            .order_by("-created_at")[:20]
        )
        spins = [
            {
                "id": sp.id,
                "created_at": sp.created_at,
                "case": {"id": sp.case_id, "name": sp.case.name},
                "prize": {
                    "id": sp.case_prize_id or sp.prize_id, 
                    "title": (
                        (sp.case_prize.prize.name if sp.case_prize and sp.case_prize.prize else None) or
                        (sp.case_prize.title if sp.case_prize and sp.case_prize.title else None) or
                        (sp.prize.title if sp.prize else None) or
                        "Неизвестный приз"
                    ), 
                    "amount_usd": sp.actual_amount_usd or (sp.prize.amount_usd if sp.prize else 0)
                },
            }
            for sp in spins_qs
        ]

        # deposits history
        deposits_qs = (
            Deposit.objects.filter(user=user)
            .select_related("status")
            .order_by("-created_at")
        )
        deposits = [
            {
                "id": dep.id,
                "amount_usd": float(dep.amount_usd),
                "method": dep.method,
                "details": dep.details,
                "status": {"code": dep.status.code, "name": dep.status.name},
                "created_at": dep.created_at,
                "processed_at": dep.processed_at,
                "comment": dep.comment,
            }
            for dep in deposits_qs
        ]

        # withdrawals history
        withdrawals_qs = (
            Withdrawal.objects.filter(user=user)
            .select_related("status")
            .order_by("-created_at")
        )
        withdrawals = [
            {
                "id": wd.id,
                "amount_usd": float(wd.amount_usd),
                "method": wd.method,
                "details": wd.details,
                "status": {"code": wd.status.code, "name": wd.status.name},
                "created_at": wd.created_at,
                "processed_at": wd.processed_at,
                "comment": wd.comment,
            }
            for wd in withdrawals_qs
        ]

        # Подсчет подтвержденных депозитов и выводов
        approved_deposit_status = DepositStatus.objects.filter(code="approved").first()
        approved_withdrawal_status = WithdrawalStatus.objects.filter(code="approved").first()
        
        approved_deposits_total = 0.0
        approved_withdrawals_total = 0.0
        
        if approved_deposit_status:
            approved_deposits_total = float(
                Deposit.objects.filter(user=user, status=approved_deposit_status)
                .aggregate(total=models.Sum('amount_usd'))['total'] or 0.0
            )
            
        if approved_withdrawal_status:
            approved_withdrawals_total = float(
                Withdrawal.objects.filter(user=user, status=approved_withdrawal_status)
                .aggregate(total=models.Sum('amount_usd'))['total'] or 0.0
            )

        # Получение активных блокировок пользователя
        withdrawal_blocks = WithdrawalBlock.objects.filter(user=user, is_active=True)
        deposit_blocks = DepositBlock.objects.filter(user=user, is_active=True)
        account_blocks = AccountBlock.objects.filter(user=user, is_active=True)
        
        blocks_data = {
            "withdrawal": WithdrawalBlockSerializer(withdrawal_blocks, many=True).data,
            "deposit": DepositBlockSerializer(deposit_blocks, many=True).data,
            "account": AccountBlockSerializer(account_blocks, many=True).data,
        }

        return Response({
            "user": self.get_serializer(user).data,
            "referrals": {
                "level1_percent": level1_percent,
                "level2_percent": level2_percent,
                "level1": ser_ref(l1, include_referrer=False, percent=level1_percent),
                "level2": ser_ref(l2, include_referrer=True, percent=level2_percent),
            },
            "spins": spins,
            "deposits": deposits,
            "withdrawals": withdrawals,
            "approved_deposits_total": approved_deposits_total,
            "approved_withdrawals_total": approved_withdrawals_total,
            "blocks": blocks_data,
        })

    @action(detail=True, methods=["get"], url_path="spins")
    def spins_history(self, request, pk=None):
        """Отдельный endpoint для получения истории круток с пагинацией"""
        user = self.get_object()
        
        # Параметры пагинации
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        
        # Запрос круток (показываем все, дополнительные открытия в отдельной таблице BonusSpin)
        spins_qs = (
            Spin.objects.filter(user=user)
            .select_related("case", "prize")
            .prefetch_related("bonus_spin_records")
            .order_by("-created_at")
        )
        
        total_spins = spins_qs.count()
        start = (page - 1) * page_size
        end = start + page_size
        
        spins_page = spins_qs[start:end]
        spins = [
            {
                "id": sp.id,
                "created_at": sp.created_at,
                "case": {"id": sp.case_id, "name": sp.case.name},
                "prize": {
                    "id": sp.case_prize_id or sp.prize_id, 
                    "title": (
                        (sp.case_prize.prize.name if sp.case_prize and sp.case_prize.prize else None) or
                        (sp.case_prize.title if sp.case_prize and sp.case_prize.title else None) or
                        (sp.prize.title if sp.prize else None) or
                        "Неизвестный приз"
                    ), 
                    "amount_usd": sp.actual_amount_usd or (sp.prize.amount_usd if sp.prize else 0)
                },
            }
            for sp in spins_page
        ]
        
        pagination = {
            "page": page,
            "page_size": page_size,
            "total": total_spins,
            "total_pages": (total_spins + page_size - 1) // page_size,
            "has_next": end < total_spins,
            "has_previous": page > 1
        }

        return Response({
            "spins": spins,
            "pagination": pagination,
        })

    @action(detail=True, methods=["post"], url_path="blocks/withdrawal")
    def create_withdrawal_block(self, request, pk=None):
        """Создать блокировку вывода для пользователя"""
        user = self.get_object()
        data = request.data.copy()
        data['user'] = user.id
        
        serializer = WithdrawalBlockCreateSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            block = serializer.save()
            return Response(WithdrawalBlockSerializer(block).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="blocks/deposit")
    def create_deposit_block(self, request, pk=None):
        """Создать блокировку ввода для пользователя"""
        user = self.get_object()
        data = request.data.copy()
        data['user'] = user.id
        
        serializer = DepositBlockCreateSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            block = serializer.save()
            return Response(DepositBlockSerializer(block).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="blocks/account")
    def create_account_block(self, request, pk=None):
        """Создать блокировку аккаунта для пользователя"""
        user = self.get_object()
        data = request.data.copy()
        data['user'] = user.id
        
        serializer = AccountBlockCreateSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            block = serializer.save()
            return Response(AccountBlockSerializer(block).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["delete"], url_path="blocks/withdrawal/(?P<block_id>[^/.]+)")
    def remove_withdrawal_block(self, request, pk=None, block_id=None):
        """Удалить блокировку вывода пользователя"""
        user = self.get_object()
        try:
            block = WithdrawalBlock.objects.get(id=block_id, user=user, is_active=True)
            block.is_active = False
            block.save()
            return Response({"detail": "Блокировка вывода успешно удалена"}, status=status.HTTP_200_OK)
        except WithdrawalBlock.DoesNotExist:
            return Response({"detail": "Блокировка вывода не найдена"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["delete"], url_path="blocks/deposit/(?P<block_id>[^/.]+)")
    def remove_deposit_block(self, request, pk=None, block_id=None):
        """Удалить блокировку ввода пользователя"""
        user = self.get_object()
        try:
            block = DepositBlock.objects.get(id=block_id, user=user, is_active=True)
            block.is_active = False
            block.save()
            return Response({"detail": "Блокировка ввода успешно удалена"}, status=status.HTTP_200_OK)
        except DepositBlock.DoesNotExist:
            return Response({"detail": "Блокировка ввода не найдена"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["delete"], url_path="blocks/account/(?P<block_id>[^/.]+)")
    def remove_account_block(self, request, pk=None, block_id=None):
        """Удалить блокировку аккаунта пользователя"""
        user = self.get_object()
        try:
            block = AccountBlock.objects.get(id=block_id, user=user, is_active=True)
            block.is_active = False
            block.save()
            return Response({"detail": "Блокировка аккаунта успешно удалена"}, status=status.HTTP_200_OK)
        except AccountBlock.DoesNotExist:
            return Response({"detail": "Блокировка аккаунта не найдена"}, status=status.HTTP_404_NOT_FOUND)


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


class AdminPromocodeViewSet(viewsets.ModelViewSet):
    queryset = Promocode.objects.all().order_by("-created_at")
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return AdminPromocodeWriteSerializer
        return AdminPromocodeSerializer


class AdminPromocodeActivationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        PromocodeActivation.objects.select_related("promocode", "user")
        .order_by("-created_at", "-id")
    )
    serializer_class = AdminPromocodeActivationSerializer
    permission_classes = [IsAdmin]

