import math
import logging
logger = logging.getLogger(__name__)

from django.contrib.gis.geos import GEOSGeometry

OFFSET = 268435456
RADIUS = 85445659.4471

def iround(x):
    """iround(number) -> integer
    Round a number to the nearest integer."""
    return int(round(x) - .5) + (x > 0)

def lonToX(lon):
    return iround(OFFSET + RADIUS * lon * math.pi / 180)

def latToY(lat):
    return iround(OFFSET - RADIUS * 
                math.log((1 + math.sin(lat * math.pi / 180)) / 
                (1 - math.sin(lat * math.pi / 180))) / 2)

def p_pixelDistance(lat1, lon1, lat2, lon2, zoom):
    x1 = lonToX(lon1);
    y1 = latToY(lat1);

    x2 = lonToX(lon2);
    y2 = latToY(lat2);
    distance = math.sqrt(math.pow((x1-x2),2) + math.pow((y1-y2),2))
    #print(iround(distance), iround(distance) >> (21 - zoom), (21 - zoom))
    logger.info("p_pixelDistance Compute distance in pixel between points : %s px" % (iround(distance) >> (21 - zoom)))
    return iround(distance) >> (21 - zoom)

def pixelDistance(point1, point2, zoom):
    pt1 = point1.transform(27561, clone=True)
    pt2 = point2.transform(27561, clone=True)
    distance = pt1.distance(pt2)
    logger.info('Compute distance between 2 points : %s miles %s pixels' % (distance, iround(distance) >> (21 - zoom)))
    return iround(distance) >> (21 - zoom)


def cluster_latlng(cluster):
    n = len(cluster)
    xyz_coords = [[math.cos(item.position.x)*math.cos(item.position.y), 
          math.cos(item.position.x)*math.sin(item.position.y), 
          math.sin(item.position.x)] for item in cluster]
    x = sum([i[0] for i in xyz_coords])/n
    y = sum([i[1] for i in xyz_coords])/n
    z = sum([i[2] for i in xyz_coords])/n
    lng = math.atan2(y, x)
    hyp = math.sqrt(x * x + y * y)
    lat = math.atan2(z, hyp)
    return {'lat':lat, 'lng':lng}

def cluster(markers, distance, zoom):
    clustered = []
    # Loop until all markers have been compared.
    markers = list(markers)
    while len(markers):
        marker  = markers.pop();
        cluster = []
        # Compare against all markers which are left.
        for idx, target in enumerate(markers):
            #pixels = pixelDistance(marker.position.x, marker.position.y,
            #                        target.position.x, target.position.y,
            #                        zoom)
            pixels = pixelDistance(marker.position, target.position, zoom)
            pixels2 = p_pixelDistance(marker.position.y, marker.position.x, target.position.y, target.position.x, zoom)
            # If two markers are closer than given distance remove
            # target marker from array and add it to cluster. 
            #print(distance, pixels, zoom)   
            if distance > pixels2:
                #print("Distance between %s,%s and %s,%s is %s pixels.\n" %
                #    (marker.position.x, marker.position.y,
                #    target.position.x, target.positino.y,
                #    pixels))
                markers.pop(idx)
                cluster.append(target)

        #If a marker has been added to cluster, add also the one 
        #we were comparing to and remove the original from array.
        if len(cluster) > 0:
            cluster.append(marker)
            clustered.append(cluster)
        else:
            clustered.append(marker)
    
    return clustered

def clust(north_east_lat, north_east_lng, south_west_lat, south_west_lng, model):
    logger.info("call clust function")
    point_1 = '%s %s' % (north_east_lng, north_east_lat)
    point_2 = '%s %s' % (south_west_lng, north_east_lat)
    point_3 = '%s %s' % (south_west_lng, south_west_lat)
    point_4 = '%s %s' % (north_east_lng, south_west_lat)
    logger.info("%s %s %s %s" % (point_1, point_2, point_3, point_4))
    bounds = GEOSGeometry('POLYGON(( %s, %s, %s, %s, %s))' % 
                          (point_1, point_2, point_3, point_4, point_1))
    logger.info("bounds %s" % (bounds))
    
    qs = model.objects.filter(position__within = bounds)
    total = qs.count()
    logger.info("total %s" % (total))
    if total > 1:
        # cluster
        logger.info('> sup a 1')
        centroid = qs.collect().envelope.centroid
        return {'type':'cluster', 'lat':centroid.y, 'lng':centroid.x, 'total':total}
    if total == 1:
        return {'type':'marker', 'lat':qs[0].position.y, 'lng':qs[0].position.x, 'item_id':qs[0].item_id} 
    return None
    
    '''
    point_1lat = '%s' % (north_east_lat)
    point_1lng = '%s' % (north_east_lng)
    point_2lat = '%s' % (north_east_lat)
    point_2lng = '%s' % (south_west_lng)
    point_3lat = '%s' % (south_west_lat)
    point_3lng = '%s' % (south_west_lng)
    point_4lat = '%s' % (south_west_lat)
    point_4lng = '%s' % (north_east_lng)
    return {'point_1lat':point_1lat, 'point_2lat':point_2lat, 'point_3lat':point_3lat, 'point_4lat':point_4lat, 
            'point_1lng':point_1lng, 'point_2lng':point_2lng, 'point_3lng':point_3lng, 'point_4lng':point_4lng}
    '''