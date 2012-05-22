import datetime
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.forms.models import inlineformset_factory
from utils.models import ItemLocation
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.models import User
from utils.forms import ItemLocationForm
from urllib2 import urlopen
from django.utils import simplejson

def get_client_ip(request):
    """
    Get client IP, used to localize client
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_lat_lon_client(ip):
    """
    Get latitude and longitude based on freegeoip service
    """
    try:
        url = 'http://freegeoip.net/json/%s' % (ip)
        data = simplejson.load(urlopen(url))
        lat = float(data['latitude'])
        lon = float(data['longitude'])
        if lat == 0.0 or lon == 0.0:
            lat, lon = 48.833, 2.333
        return lat, lon
    except:
        return 48.833, 2.333

def home(request):
    ip = get_client_ip(request)
    lat, lon = get_lat_lon_client(ip)
    ItemLocationFormset = inlineformset_factory(User, ItemLocation,
                                                       form=ItemLocationForm, extra=0)
    formset = ItemLocationFormset()
    if request.method == "POST":
        user = request.user
        formset = ItemLocationFormset(request.POST, instance=user)
        if formset.is_valid():
            formset.save()
    if request.user.is_authenticated():
        formset = ItemLocationFormset(instance=request.user)

    return render_to_response('index.html',
                           {'formset':formset, 'lat':lat, 'lon':lon },
                          context_instance=RequestContext(request))

def logout_view(request):
    logout(request)
    return redirect('home')
    