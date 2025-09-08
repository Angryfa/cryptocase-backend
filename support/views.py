from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Ticket, TicketMessage, TicketStatus
from .serializers import (
    TicketSerializer,
    TicketCreateSerializer,
    TicketReplySerializer,
)


class IsAdminOrReadOnly(permissions.IsAdminUser):
    pass


class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Ticket.objects.select_related("user").all()
        return Ticket.objects.select_related("user").filter(user=user)

    def get_serializer_class(self):
        if self.action == "create":
            return TicketCreateSerializer
        return TicketSerializer

    def create(self, request, *args, **kwargs):
        # Используем отдельный сериализатор для создания (с body/attachment),
        # а в ответ отдаем полноценный TicketSerializer
        s = TicketCreateSerializer(data=request.data, context={"request": request})
        s.is_valid(raise_exception=True)
        ticket = s.save()
        out = TicketSerializer(ticket, context=self.get_serializer_context())
        headers = self.get_success_headers(out.data)
        return Response(out.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=["post"], url_path="reply")
    def reply(self, request, pk=None):
        ticket = self.get_object()
        if ticket.status == TicketStatus.CLOSED:
            return Response({"detail": "Тикет закрыт"}, status=status.HTTP_400_BAD_REQUEST)
        s = TicketReplySerializer(data=request.data, context={"request": request, "ticket": ticket})
        s.is_valid(raise_exception=True)
        msg = s.save()
        return Response(TicketSerializer(ticket, context=self.get_serializer_context()).data)

    @action(detail=True, methods=["post"], url_path="close")
    def close(self, request, pk=None):
        ticket = self.get_object()
        ticket.status = TicketStatus.CLOSED
        if request.user.is_staff or request.user.is_superuser:
            ticket.is_closed_by_staff = True
        else:
            ticket.is_closed_by_user = True
        ticket.save(update_fields=["status", "is_closed_by_staff", "is_closed_by_user", "updated_at"])
        return Response(TicketSerializer(ticket, context=self.get_serializer_context()).data)

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        ticket = self.get_object()
        is_staff = request.user.is_staff or request.user.is_superuser
        now = timezone.now()
        updated = 0
        for m in ticket.messages.all():
            if is_staff:
                if m.read_by_staff_at is None:
                    m.read_by_staff_at = now
                    m.save(update_fields=["read_by_staff_at"])
                    updated += 1
            else:
                if m.author_id != request.user.id and m.read_by_user_at is None:
                    m.read_by_user_at = now
                    m.save(update_fields=["read_by_user_at"])
                    updated += 1
        return Response({"updated": updated})


