from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q, Sum
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .models import Profile, Withdrawal, WithdrawalStatus, Deposit, DepositStatus
from .serializers import UserPublicSerializer, RegisterSerializer, ProfileSerializer, UserWithProfileSerializer
from django.utils import timezone
from referrals.models import ReferralProfile

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        s = RegisterSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        email = s.validated_data["email"].lower()
        password = s.validated_data["password"]

        # username = email (для базовой модели User)
        if User.objects.filter(Q(username=email) | Q(email=email)).exists():
            return Response({"error": "Пользователь уже существует"}, status=400)

        user = User.objects.create_user(username=email, email=email, password=password)

       # --- реферальная привязка (без бонусов) ---
        ref_code = (request.data.get("ref") or "").strip()
        if ref_code:
            try:
                referrer_profile = ReferralProfile.objects.select_related("user").get(code=ref_code)
                # профиль нового пользователя создаётся сигналом пост-сейва; на всякий случай подстрахуемся:
                my_ref_profile, _ = ReferralProfile.objects.get_or_create(user=user)
                # защита от самопривязки (на всякий случай)
                if referrer_profile.user_id != user.id:
                    my_ref_profile.referred_by = referrer_profile.user
                    my_ref_profile.referred_at = timezone.now()
                    my_ref_profile.save(update_fields=["referred_by", "referred_at"])
            except ReferralProfile.DoesNotExist:
                pass
        # ------------------------------------------

        data = UserPublicSerializer(user).data
        return Response({"user": data}, status=201)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").lower().strip()
        password = request.data.get("password") or ""

        if not email or not password:
            return Response({"error": "Введите email и пароль"}, status=400)

        # базовый authenticate принимает username, поэтому ищем по email
        username = email
        user = authenticate(request, username=username, password=password)
        if not user:
            # попробуем найти по email и подставить username (на случай если username != email)
            try:
                u = User.objects.get(email=email)
                user = authenticate(request, username=u.username, password=password)
            except User.DoesNotExist:
                pass

        if not user:
            return Response({"error": "Неверный email или пароль"}, status=401)

        refresh = RefreshToken.for_user(user)
        data_user = UserPublicSerializer(user).data
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": data_user,
        })


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        return Response(UserWithProfileSerializer(request.user).data)


# refresh = стандартный simplejwt
class RefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]

class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def _add_withdrawn_total(self, request, data: dict) -> dict:
        # Находим статус "approved" и считаем сумму всех подтверждённых выводов пользователя
        approved = WithdrawalStatus.objects.filter(code="approved").first()
        total = Decimal("0.00")
        if approved:
            total = (
                Withdrawal.objects
                .filter(user=request.user, status=approved)
                .aggregate(s=Sum("amount_usd"))["s"]
                or Decimal("0.00")
            )
        data["withdrawn_total_usd"] = total
        return data
    #Подсчет депоизта и вывода
    def _add_fin_totals(self, request, data: dict) -> dict:
        dep_ok = DepositStatus.objects.filter(code="approved").first()
        wdr_ok = WithdrawalStatus.objects.filter(code="approved").first()
        deposit_total = Decimal("0.00")
        withdrawn_total = Decimal("0.00")
        if dep_ok:
            deposit_total = (
               Deposit.objects
               .filter(user=request.user, status=dep_ok)
               .aggregate(s=Sum("amount_usd"))["s"]
               or Decimal("0.00")
            )
        if wdr_ok:
            withdrawn_total = (
               Withdrawal.objects
               .filter(user=request.user, status=wdr_ok)
               .aggregate(s=Sum("amount_usd"))["s"]
               or Decimal("0.00")
            )
        data["deposit_total_usd"] = deposit_total
        data["withdrawn_total_usd"] = withdrawn_total
        return data
        
                

    def get(self, request):
        prof, _ = Profile.objects.get_or_create(user=request.user)
        data = ProfileSerializer(prof).data
        return Response(self._add_fin_totals(request, data))

    def patch(self, request):
        prof, _ = Profile.objects.get_or_create(user=request.user)
        s = ProfileSerializer(prof, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        prof = s.save()
        data = ProfileSerializer(prof).data
        return Response(self._add_fin_totals(request, data))