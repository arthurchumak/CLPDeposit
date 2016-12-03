# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from app.management.commands import pay, rates
from app.models import Setting


class Command(BaseCommand):
    def handle(self, *args, **options):
        Setting.set_processing(True)
        days = Setting.objects.get_or_create(name='days')[0]
        days.value += 1
        days.save()
        rates.Command().handle()
        pay.Command().handle()
        Setting.set_processing(False)
