# coding=utf-8

from django.db import models
from django.contrib.auth.models import User
import ast

class ItemLocation(models.Model):
    ITEM_CHOICES = (
        ('artist', 'Artist'),
        ('track', 'Track'),
        ('album', 'Album'),
    )
    item_type = models.CharField(max_length=5, choices=ITEM_CHOICES)
    item_id = models.IntegerField()
    position = models.CharField(max_length=255)
    user = models.ForeignKey(User)
    # TODO? comment = models.TextField(blank=True, null=True)
    # TODO? add unique for item_id, item, user
    # TODO: add lat and lon as fields
    # TODO: add label (to prevent reload data from deezer)
    # TODO: add artist image
    def _get_lat(self):
        return ast.literal_eval(self.position)[0]
    lat = property(_get_lat)
    def _get_lon(self):
        return ast.literal_eval(self.position)[1]
    lon = property(_get_lon)