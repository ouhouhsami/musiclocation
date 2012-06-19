import datetime

import factory
from models import SongLocation
from django.contrib.auth.models import User
import random

class UserFactory(factory.Factory):
    FACTORY_FOR = User

    #@classmethod
    #def _setup_next_sequence(cls):
    #    try:
    #        return cls._associated_class.objects.values_list(
    #            'id', flat=True).order_by('-id')[0] + 1
    #    except IndexError:
    #        return 0

    username = factory.Sequence(lambda n: "username%s" % n)
    first_name = factory.Sequence(lambda n: "first_name%s" % n)
    last_name = factory.Sequence(lambda n: "last_name%s" % n)
    email = factory.Sequence(lambda n: "email%s@example.com" % n)
    password = 'sha1$caffc$30d78063d8f2a5725f60bae2aca64e48804272c3'
    is_staff = False
    is_active = True
    is_superuser = False
    last_login = datetime.datetime(2000, 1, 1)
    date_joined = datetime.datetime(1999, 1, 1)

def random_location(n):
    point = "POINT (%s %s)" % (random.uniform(-180, 180), random.uniform(-90, 90))
    print point
    return point


class SongLocationFactory(factory.Factory):
    FACTORY_FOR = SongLocation

    user = factory.LazyAttribute(lambda a: UserFactory())
    item_id = factory.Sequence(lambda n: n)
    position = factory.Sequence(random_location)
