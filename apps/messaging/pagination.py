"""Пагинация списка диалогов."""

from apps.common.pagination import DefaultCursorPagination


class ConversationCursorPagination(DefaultCursorPagination):
    ordering = ("-last_message_at", "-id")
