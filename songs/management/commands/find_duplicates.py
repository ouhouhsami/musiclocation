from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from songs.models import SongLocation
from django.db import connection

class Command(BaseCommand):
    def handle(self, *args, **options):
        #user = User.objects.get(id=1)
        #root_items = SongLocation.objects.filter(user=user)
        #root_items.delete()
        #items = SongLocation.objects.raw('SELECT item_id, count(*) from utils_itemlocation GROUP BY item_id HAVING count(*) > 1')
        cursor = connection.cursor()
        cursor.execute('''SELECT item_id, position, count(*) from utils_itemlocation GROUP BY position HAVING count(*) > 1''')
        print len(cursor.fetchall())
        for i in cursor.fetchall():
            il = SongLocation.objects.filter(item_id=i[0])
            print il[0].json['title']
        #print items.count()