# cashback/management/commands/run_cashback.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal

from cashback.services import run_cashback_snapshot

class Command(BaseCommand):
    help = "Рассчитать кэшбэк на конкретный момент времени (без слотов)."

    def add_arguments(self, parser):
        parser.add_argument("--at", type=str, default=None,
                            help="ISO datetime, e.g. '2025-09-13T16:27:00Z' (default: now)")
        parser.add_argument("--percent", type=str, default=None,
                            help="Override percent for this run, e.g. '10.0'")
        parser.add_argument("--dry-run", action="store_true", help="Do not write to DB")
        parser.add_argument("--upsert", action="store_true", help="Update if record already exists")

    def handle(self, *args, **opts):
        res = run_cashback_snapshot(
            as_of=opts.get("at"),
            percent=opts.get("percent"),
            upsert=opts.get("upsert"),
            dry_run=opts.get("dry_run"),
        )
        if not res.get("ok"):
            self.stdout.write(self.style.ERROR(res.get("error") or "Unknown error"))
            return
        self.stdout.write(self.style.SUCCESS(
            f"Cashback snapshot @ {res['as_of']} | percent={res['percent']}% | "
            f"created={res['created']}, updated={res['updated']}, skipped={res['skipped']}, dry_run={res['dry_run']}"
        ))
