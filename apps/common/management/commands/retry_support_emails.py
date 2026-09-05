import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.common.models import SupportTicket
from apps.common.services import notify_staff_about_ticket

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Повторяет отправку SupportTicket, которые не удалось доставить (SMTP timeout/error)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=50,
            help="Максимальное количество писем за один запуск",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        
        tickets = SupportTicket.objects.filter(
            email_status__in=[
                SupportTicket.EmailStatus.PENDING,
                SupportTicket.EmailStatus.FAILED,
            ]
        ).order_by("created_at")[:limit]
        
        if not tickets:
            self.stdout.write(self.style.SUCCESS("Нет обращений для повторной отправки."))
            return
            
        success_count = 0
        failed_count = 0
        
        for ticket in tickets:
            self.stdout.write(f"Отправка обращения #{ticket.pk}...")
            try:
                notify_staff_about_ticket(ticket)
                success_count += 1
                self.stdout.write(self.style.SUCCESS(f" Успешно #{ticket.pk}"))
            except Exception as e:
                failed_count += 1
                self.stdout.write(self.style.ERROR(f" Ошибка #{ticket.pk}: {e}"))
                
        self.stdout.write(
            self.style.SUCCESS(
                f"\nЗавершено. Успешно: {success_count}, Ошибок: {failed_count}"
            )
        )
