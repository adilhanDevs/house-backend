"""Бизнес-операции диалогов."""

from typing import Any

from django.db import IntegrityError, transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404

from apps.catalog.covers import COVER_ATTR, cover_candidates, listing_cover_file
from apps.catalog.enums import ListingStatus
from apps.catalog.models import Listing
from apps.common.exceptions import ConflictError
from apps.messaging.models import Conversation


def _cover_url(listing: Listing) -> str:
    cover = listing_cover_file(listing)
    return cover.url if cover else ""


def open_conversation(*, user: Any, listing_slug: str) -> tuple[Conversation, bool]:
    """Открывает один диалог покупателя с продавцом по активному объявлению."""
    listing = get_object_or_404(
        Listing.objects.filter(status=ListingStatus.ACTIVE)
        .select_related("owner")
        .prefetch_related(Prefetch("media", queryset=cover_candidates(), to_attr=COVER_ATTR)),
        slug=listing_slug,
    )
    if listing.owner_id == user.id:
        raise ConflictError("Нельзя написать самому себе.")

    lookup = {"listing": listing, "buyer": user, "seller": listing.owner}
    defaults = {
        "listing_slug": listing.slug,
        "listing_title": listing.address.strip() or listing.get_kind_display(),
        "listing_price": listing.price,
        "listing_currency": listing.currency,
        "listing_cover_url": _cover_url(listing),
    }
    with transaction.atomic():
        try:
            with transaction.atomic():
                return Conversation.objects.get_or_create(**lookup, defaults=defaults)
        except IntegrityError:
            conversation = Conversation.objects.select_related("buyer", "seller", "listing").get(
                **lookup
            )
            return conversation, False
