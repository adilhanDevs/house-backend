"""API открытия и чтения диалогов."""

from typing import Any

from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.messaging.models import Conversation
from apps.messaging.pagination import ConversationCursorPagination
from apps.messaging.selectors import conversation_for_participant, conversations_for
from apps.messaging.serializers import ConversationCreateSerializer, ConversationSerializer
from apps.messaging.services import open_conversation


class ConversationListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = ConversationCursorPagination
    serializer_class = ConversationSerializer
    queryset = Conversation.objects.none()

    def get_queryset(self):  # noqa: ANN201
        if not self.request.user.is_authenticated:  # pragma: no cover - генерация схемы
            return Conversation.objects.none()
        return conversations_for(self.request.user)

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        incoming = ConversationCreateSerializer(data=request.data)
        incoming.is_valid(raise_exception=True)
        conversation, created = open_conversation(
            user=request.user,
            listing_slug=incoming.validated_data["listing_slug"],
        )
        conversation = conversation_for_participant(
            user=request.user,
            conversation_id=conversation.id,
        )
        return Response(
            ConversationSerializer(conversation, context={"request": request}).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class ConversationDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationSerializer
    queryset = Conversation.objects.none()

    def get_object(self) -> Conversation:
        return conversation_for_participant(
            user=self.request.user,
            conversation_id=self.kwargs["conversation_id"],
        )
