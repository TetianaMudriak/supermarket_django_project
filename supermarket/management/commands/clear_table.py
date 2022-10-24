from django.core.management.base import BaseCommand, CommandError

from supermarket.table_cleaner import main


class Command(BaseCommand):
    help = 'Clear data from tables'

    def handle(self, *args, **options):
        try:
            main()
        except Exception as error:
            raise CommandError('Error happen when clearing %s' % error)

        self.stdout.write(self.style.SUCCESS(
            'Tables successfully cleared')
        )
