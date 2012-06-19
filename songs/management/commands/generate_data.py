from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from songs.models import SongLocation
from songs.factories import SongLocationFactory

class Command(BaseCommand):
    def handle(self, *args, **options):
        User.objects.exclude(id=1).delete()
        SongLocation.objects.all().delete()
        user = User.objects.get(id=1)
        SongLocationFactory.create_batch(10000)
