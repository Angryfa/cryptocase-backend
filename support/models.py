from django.conf import settings
from django.db import models
from django.utils import timezone
import os
import uuid


User = settings.AUTH_USER_MODEL


class TicketStatus(models.TextChoices):
    OPEN = "open", "Открыт"
    ANSWERED = "answered", "Отвечен"
    CLOSED = "closed", "Закрыт"


def upload_to_ticket(instance, filename: str) -> str:
    # Безопасное имя файла: только базовое имя и новый uuid
    base = os.path.basename(filename or "")
    _name, ext = os.path.splitext(base)
    ext = (ext or "").lower()
    new_name = f"{uuid.uuid4().hex}{ext}"
    return f"support/{instance.ticket_id}/{new_name}"


class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tickets")
    subject = models.CharField(max_length=200)
    status = models.CharField(max_length=16, choices=TicketStatus.choices, default=TicketStatus.OPEN, db_index=True)
    is_closed_by_user = models.BooleanField(default=False)
    is_closed_by_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at", "-id")

    def __str__(self):
        return f"Ticket<{self.id}> {self.subject} [{self.status}]"


class TicketMessage(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="messages")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ticket_messages")
    body = models.TextField()
    attachment = models.FileField(upload_to=upload_to_ticket, blank=True, null=True)

    # Отметки чтения: когда staff/admin увидел и когда пользователь увидел
    read_by_user_at = models.DateTimeField(null=True, blank=True)
    read_by_staff_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at", "id")

    def __str__(self):
        return f"Msg<{self.id}> t={self.ticket_id} by={self.author_id}"

