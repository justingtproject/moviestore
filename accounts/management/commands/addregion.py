from django.core.management.base import BaseCommand
from accounts.models import Region

class Command(BaseCommand):
    help = 'Add a region to the database.'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Region name')
        parser.add_argument('code', type=str, help='Region code')
        parser.add_argument('latitude', type=float, help='Latitude')
        parser.add_argument('longitude', type=float, help='Longitude')

    def handle(self, *args, **options):
        name = options['name']
        code = options['code']
        latitude = options['latitude']
        longitude = options['longitude']
        region, created = Region.objects.get_or_create(
            name=name,
            defaults={'code': code, 'latitude': latitude, 'longitude': longitude}
        )
        if not created:
            self.stdout.write(self.style.WARNING(f'Region "{name}" already exists.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Region "{name}" added successfully.'))
