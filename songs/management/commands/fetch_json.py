from urllib2 import urlopen

from django.core.management.base import BaseCommand, CommandError
from django.utils import simplejson

from songs.models import SongLocation

class Command(BaseCommand):

    def handle(self, *args, **options):
        for instance in SongLocation.objects.all():
            url = 'http://api.deezer.com/2.0/%s/%s' % (instance.item_type, instance.item_id)
            data = simplejson.load(urlopen(url))
            instance.json = data
            instance.save()