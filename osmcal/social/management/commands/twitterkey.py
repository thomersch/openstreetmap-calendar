from django.core.management.base import BaseCommand
from osmcal.social import twitter


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--verifier',
            type=str
        )

    def handle(self, *args, **options):
        if options.get('verifier', None):
            twitter.auth_keys(options['verifier'])
        else:
            twitter.auth_initialize()
