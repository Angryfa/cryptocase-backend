from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .models import CashbackAccrual

class MyCashbackListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = CashbackAccrual.objects.filter(user=request.user).order_by("-slot_started_at")[:200]
        items = [{
            "amount_usd": str(x.amount_usd),
            "slot_started_at": x.slot_started_at,
            "computed_at": x.computed_at,
            "status": x.status,
        } for x in qs]
        return Response({"items": items})