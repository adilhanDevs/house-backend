"""Оптимизированные выборки диалогов."""

from typing import Any

from django.db.models import (
    CharField,
    Count,
    DateTimeField,
    F,
    IntegerField,
    OuterRef,
    Q,
    QuerySet,
    Subquery,
    UUIDField,
)
from django.shortcuts import get_object_or_404

from apps.messaging.models import Conversation, Message


def _conversation_queryset(user: Any) -> QuerySet[Conversation]:
    latest = Message.objects.filter(conversation_id=OuterRef("pk")).order_by("-created_at", "-id")
    unread = (
        Q(buyer=user, buyer_last_read_at__isnull=True)
        | Q(buyer=user, messages__created_at__gt=F("buyer_last_read_at"))
        | Q(seller=user, seller_last_read_at__isnull=True)
        | Q(seller=user, messages__created_at__gt=F("seller_last_read_at"))
    )
    return (
        Conversation.objects.filter(Q(buyer=user) | Q(seller=user))
        .select_related("buyer", "seller", "listing")
        .annotate(
            latest_message_id=Subquery(latest.values("id")[:1], output_field=UUIDField()),
            latest_message_sender_id=Subquery(
                latest.values("sender_id")[:1], output_field=IntegerField()
            ),
            latest_message_text=Subquery(latest.values("text")[:1], output_field=CharField()),
            latest_message_created_at=Subquery(
                latest.values("created_at")[:1], output_field=DateTimeField()
            ),
            unread_count=Count("messages", filter=unread),
        )
        .order_by("-last_message_at", "-id")
    )


def conversations_for(user: Any) -> QuerySet[Conversation]:
    """Все диалоги участника с peer, latest message и unread без N+1."""
    return _conversation_queryset(user)


def conversation_for_participant(*, user: Any, conversation_id: Any) -> Conversation:
    """Диалог виден только его покупателю или продавцу."""
    return get_object_or_404(_conversation_queryset(user), pk=conversation_id)
