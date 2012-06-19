from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from songs.models import SongLocation

class Command(BaseCommand):
    def handle(self, *args, **options):
        #user = User.objects.get(id=1)
        #root_items = SongLocation.objects.filter(user=user)
        #root_items.delete()
        SongLocation.objects.all().delete()