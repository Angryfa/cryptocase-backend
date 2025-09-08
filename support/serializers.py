from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from .models import Ticket, TicketMessage, TicketStatus


User = get_user_model()


class TicketMessageSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TicketMessage
        fields = (
            "id",
            "ticket",
            "author",
            "body",
            "attachment",
            "read_by_user_at",
            "read_by_staff_at",
            "created_at",
        )
        read_only_fields = ("ticket", "author", "read_by_user_at", "read_by_staff_at", "created_at")

    def get_author(self, obj):
        return {"id": obj.author_id, "email": getattr(obj.author, "email", None), "username": getattr(obj.author, "username", None)}

    def validate_attachment(self, f):
        if not f:
            return f
        allowed = {"application/pdf", "image/jpeg", "image/png"}
        # content_type может отсутствовать, поэтому дополнительно по расширению
        if hasattr(f, "content_type") and f.content_type:
            if f.content_type not in allowed:
                raise serializers.ValidationError("Допустимы только PDF/JPEG/PNG")
        name = f.name.lower()
        if not (name.endswith(".pdf") or name.endswith(".jpeg") or name.endswith(".jpg") or name.endswith(".png")):
            raise serializers.ValidationError("Допустимы только .pdf, .jpeg, .jpg, .png")
        # ограничение размера 10 МБ
        if f.size and f.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("Файл слишком большой (макс. 10 МБ)")
        return f


class TicketSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    messages = TicketMessageSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = (
            "id",
            "user",
            "subject",
            "status",
            "is_closed_by_user",
            "is_closed_by_staff",
            "created_at",
            "updated_at",
            "messages",
        )
        read_only_fields = ("status", "is_closed_by_user", "is_closed_by_staff", "created_at", "updated_at")

    def get_user(self, obj):
        return {"id": obj.user_id, "email": getattr(obj.user, "email", None), "username": getattr(obj.user, "username", None)}


class TicketCreateSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=200)
    body = serializers.CharField()
    attachment = serializers.FileField(required=False, allow_null=True)

    def validate_attachment(self, f):
        return TicketMessageSerializer().validate_attachment(f)

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user
        subject = validated_data["subject"]
        body = validated_data["body"]
        attachment = validated_data.get("attachment")
        ticket = Ticket.objects.create(user=user, subject=subject, status=TicketStatus.OPEN)
        TicketMessage.objects.create(ticket=ticket, author=user, body=body, attachment=attachment)
        return ticket


class TicketReplySerializer(serializers.Serializer):
    body = serializers.CharField()
    attachment = serializers.FileField(required=False, allow_null=True)

    def validate_attachment(self, f):
        return TicketMessageSerializer().validate_attachment(f)

    def save(self, **kwargs):
        request = self.context["request"]
        ticket: Ticket = self.context["ticket"]
        body = self.validated_data["body"]
        attachment = self.validated_data.get("attachment")
        msg = TicketMessage.objects.create(ticket=ticket, author=request.user, body=body, attachment=attachment)
        # Обновляем статус тикета при ответе сотрудника
        if request.user.is_staff or request.user.is_superuser:
            ticket.status = TicketStatus.ANSWERED
            ticket.save(update_fields=["status", "updated_at"])
        return msg


