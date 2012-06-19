from urllib2 import urlopen

from django.core.management.base import BaseCommand, CommandError
from django.utils import simplejson
from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry


from songs.models import SongLocation
import csv
import pprint


fieldnames = ("RC", "UFI", "UNI", "LAT", "LONG",
                  "DMS_LAT", "DMS_LONG", "MGRS", "JOG", 
                  "FC", "DSG", "PC", "CC1", "ADM1", "POP", 
                  "ELEV", "CC2", "NT", "LC", "SHORT_FORM", 
                  "GENERIC", "SORT_NAME_RO", "FULL_NAME_RO", "FULL_NAME_ND_RO", 
                  "SORT_NAME_RG", "FULL_NAME_RG", "FULL_NAME_ND_RG", "NOTE", "MODIFY_DATE")


class Command(BaseCommand):

    def handle(self, *args, **options):
        f = open('/Users/goldszmidt/sam/perso/transit/fr.txt', 'r')
        reader = csv.DictReader(f, delimiter="\t", fieldnames=fieldnames)
        user = User.objects.get(id=1)
        root_items = SongLocation.objects.filter(user=user)
        root_items.delete()
        for row in reader:
            url = 'http://api.deezer.com/2.0/search/track/?q=%s' % (row['FULL_NAME_ND_RG'])
            json = simplejson.load(urlopen(url))
            try:
                for obj in json['data']:
                    if row['FULL_NAME_ND_RO'] in obj['title']:
                        print row['FULL_NAME_ND_RG']
                        position = GEOSGeometry('POINT(%s %s)' % (row['LONG'], row['LAT']))
                        print position
                        item = SongLocation(user=user, position=position, item_id=obj['id'], json=obj)
                        item.save()
            except KeyError:
                # json has no data key
                pass