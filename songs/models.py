# coding=utf-8

from django.db import models
from django.contrib.gis.db import models
from django.contrib.auth.models import User
import ast
from django_extensions.db.fields import json


class SongLocation(models.Model):

    item_id = models.IntegerField()
    position = models.PointField(srid=4326)    
    user = models.ForeignKey(User)
    json = json.JSONField(blank=True, null=True)
    
    objects = models.GeoManager()
