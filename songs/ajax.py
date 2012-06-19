# coding=utf-8
import ast
from urllib2 import urlopen
import numpy as np
import Pycluster as pc
import json
from collections import Counter
import logging

from django.utils import simplejson
from django.core import serializers
from django.http import QueryDict 
from django.forms.models import inlineformset_factory
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.template.defaultfilters import escapejs
from django.contrib.gis.geos import GEOSGeometry, fromstr
from django.contrib.gis.measure import Distance, D

from dajaxice.core import dajaxice_functions

from songs.models import SongLocation
from songs.forms import SongLocationForm
from songs.utils import *


logger = logging.getLogger(__name__)

def hello_ajax(request): 
    ''' help test ajax function '''
    return simplejson.dumps({'message':'Hello World'})
    
dajaxice_functions.register(hello_ajax)

def get_items(request, zone):
    ''' return items to show in the map '''
    # convert string zone to python dict
    zone = ast.literal_eval(zone)
    # filter by this location
    items = SongLocation.objects.all()
    if request.user.is_authenticated():
      items = SongLocation.objects.all().exclude(user = request.user)
    inside_items = []
    for item in items:
        if item.lat > zone[0][0] and item.lat < zone[1][0] and item.lon > zone[0][1] and item.lon < zone[1][1]:
            inside_items.append(item)
    json_serializer = serializers.get_serializer("json")()
    response = json_serializer.serialize(inside_items, ensure_ascii=False)
    return response

dajaxice_functions.register(get_items)

def save_items(request, data):
    if request.user.is_authenticated():
        user = request.user
        SongLocationFormset = inlineformset_factory(User, SongLocation,
                                                       form=SongLocationForm, extra=0)
        formset = SongLocationFormset(QueryDict(data), instance=user)
        if formset.is_valid():
            formset.save()
            rendered = render_to_string('formset.html', {'formset': formset})
            return simplejson.dumps({'html':rendered})

dajaxice_functions.register(save_items)


# always check that user own updated item before deleting it or moving it
# create (item)
def save_item(request, item_id, position):
    if request.user.is_authenticated():
        user = request.user
        url = 'http://api.deezer.com/2.0/%s/%s' % ('track', item_id)
        json = simplejson.load(urlopen(url))
        item = SongLocation(item_type="track", item_id=item_id, 
                                     position=position, user=user, json=json)
        item.save()
        rendered = render_to_string('item.html', {'item': item})
        json_serializer = serializers.get_serializer("json")()
        #item.html = rendered
        item.json = simplejson.dumps(item.json)
        item_js = json_serializer.serialize([item,], ensure_ascii=False)
        return simplejson.dumps({'html':rendered, 'item_js':item_js})
        
dajaxice_functions.register(save_item)

def delete_item(request, item_id):
    if request.user.is_authenticated():
        user = request.user
        item = SongLocation.objects.get(id=item_id, user=user)
        item.delete()
        return simplejson.dumps({'message':'item deleted'})

dajaxice_functions.register(delete_item)

def is_unique(tup):
    if tup[1] == 1:
        return True
    else:
        return False

VERTICAL_STRIP = 8
HORIZONTAL_STRIP = 5


def get_songs(request, north_east_lat, north_east_lng, south_west_lat, south_west_lng, zoom):
    '''
    Get items and/or clusters for items on a map
    '''
    # filter songs inside current map
    # create the bounded region
    #logger.info('Get songs via ajax call for a zoom %s' % (zoom))
    # be careful ! lon : PointField.x lat : PointField.y
    c = []
    logger.info('longitude east and west %s %s' % (north_east_lng, south_west_lng))
    lon_step = (north_east_lng-south_west_lng)/VERTICAL_STRIP
    lat_step = (north_east_lat-south_west_lat)/HORIZONTAL_STRIP
    logger.info("lon step : %s lat_step : %s" % (lon_step, lat_step))
    for i in range(0, VERTICAL_STRIP):
        #logger.info(i)
        for j in range(0, HORIZONTAL_STRIP):
            #north_east_lat, north_east_lng, south_west_lat, south_west_lng
            point1 = north_east_lat-j*lat_step
            point2 = north_east_lng-i*lon_step
            point3 = north_east_lat-(j+1)*lat_step
            point4 = north_east_lng-(i+1)*lon_step
            #logger.info("%s %s %s %s %s" % (j, point1, point2, point3, point4))
            cluster = clust(point1, point2, point3, point4, SongLocation)
            if cluster is not None:
                c.append(cluster)
    #c = clust(north_east_lat, north_east_lng, south_west_lat, south_west_lng, SongLocation)
    logger.info(c)
    return simplejson.dumps(c)
    #point_1 = '%s %s' % (north_east_lng, north_east_lat)
    #point_2 = '%s %s' % (south_west_lng, north_east_lat)
    #point_3 = '%s %s' % (south_west_lng, south_west_lat)
    #point_4 = '%s %s' % (north_east_lng, south_west_lat)
    # create the geometry
    #bounds = GEOSGeometry('POLYGON(( %s, %s, %s, %s, %s))' % 
    #                      (point_1, point_2, point_3, point_4, point_1))
    #point_NE = fromstr("POINT(%s)" % (point_1), srid=4326)
    #point_SW = fromstr("POINT(%s)" % (point_3), srid=4326)
    # distance calculation with degree values ! ... bad
    # GEOS distance calculations are linear
    # -- in other words, GEOS does not perform a spherical calculation 
    # even if the SRID specifies a geographic coordinate system.
    #logger.info("point NE %s point SW %s" % (point_NE, point_SW))
    #logger.info("FALSE Distance between NE and SW is %s" % (point_NE.distance(point_SW)))
    # srid 27561 is for franch lambert
    #point_NE.transform(27561)
    #point_SW.transform(27561)
    # distance calculation inside new srid, it's ok, but we must know the 
    # good cartesian projection, which is different on different earth places
    #logger.info("point NE %s point SW %s" % (point_NE, point_SW))
    # not wrong distance
    #logger.info("Distance in meter between NE and SW is %s" % (point_NE.distance(point_SW)))


    # distance calculation 
    #nelng = lonToX(north_east_lng)
    #nelat = latToY(north_east_lat)
    #swlng = lonToX(south_west_lng)
    #swlat = lonToX(south_west_lat)
    #logger.info("point in cartesian format %s %s %s %s" % (nelng, nelat, swlng, swlat))
    # distance in px below is right
    #logger.info("Distance pixel between NE and SW is %s" % (p_pixelDistance(north_east_lat, north_east_lng, south_west_lat, south_west_lng, 8)))
    
    #p1 = fromstr("POINT(%s %s)" % (nelng, nelat), srid=4326)
    #p2 = fromstr("POINT(%s %s)" % (swlng, swlat), srid=4326)
    #logger.info("Distance between NE and SW is %s" % (p1.distance(p2)))

    #items = SongLocation.objects.filter(position__within = bounds)
    #clustered = cluster(items, 400, zoom);
    # update the clustered structure to return it
    #clus = []
    #total = 0
    #print clustered
    #for index, item in enumerate(clustered):
    #    if type(item) is list:
    #        n = len(item)
    #        total = total + n
    #        centroid = SongLocation.objects.filter(id__in = [song.id for song in item]).collect().envelope.centroid
    #        logger.info("Centroid is lat:%s lon:%s" % (centroid.y, centroid.x))
    #        cl = cluster_latlng(item)
    #        clustered[index] = {'type':'cluster', 'lat':centroid.y, 'lng':centroid.x, 'total':len(item)}
    #        for i in item:
    #            clus.append({'type':'marker', 'lat':i.position.y, 'lng':i.position.x, 'item_id':i.item_id})
                #logger.info({'type':'marker', 'lat':i.position.x, 'lng':i.position.y, 'item_id':i.item_id})
    #    else:
    #        total = total + 1
    #        clustered[index] = {'type':'marker', 'lat':item.position.y, 'lng':item.position.x, 'item_id':item.item_id, 'alone':True}
            #clus.append({'type':'marker', 'lat':item.position.x, 'lng':item.position.y, 'item_id':item.item_id, 'alone':True})
    #for clu in clus:
    #    clustered.append(clu)
    
    #return simplejson.dumps(clus)
    #return simplejson.dumps(clustered)

dajaxice_functions.register(get_songs)
# delete (item)
# update (position)

