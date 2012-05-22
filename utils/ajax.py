# coding=utf-8
import ast

from django.utils import simplejson
from django.core import serializers
from django.http import QueryDict 
from django.forms.models import inlineformset_factory
from django.contrib.auth.models import User
from django.template.loader import render_to_string

from dajaxice.core import dajaxice_functions

from utils.models import ItemLocation
from utils.forms import ItemLocationForm


def hello_ajax(request): 
    ''' help test ajax function '''
    return simplejson.dumps({'message':'Hello World'})
    
dajaxice_functions.register(hello_ajax)

def get_items(request, zone):
    ''' return items to show in the map '''
    # convert string zone to python dict
    zone = ast.literal_eval(zone)
    # filter by this location
    items = ItemLocation.objects.all()
    if request.user.is_authenticated():
      items = ItemLocation.objects.all().exclude(user = request.user)
    inside_items = []
    for item in items:
        if item.lat > zone[0][0] and item.lat < zone[1][0] and item.lon > zone[0][1] and item.lon < zone[1][1]:
            inside_items.append(item)
    #print items
    json_serializer = serializers.get_serializer("json")()
    response = json_serializer.serialize(inside_items, ensure_ascii=False)
    #print "here", response
    return response

dajaxice_functions.register(get_items)

def save_items(request, data):
    if request.user.is_authenticated():
        user = request.user
        ItemLocationFormset = inlineformset_factory(User, ItemLocation,
                                                       form=ItemLocationForm, extra=0)
        formset = ItemLocationFormset(QueryDict(data), instance=user)
        if formset.is_valid():
            formset.save()
            rendered = render_to_string('formset.html', {'formset': formset})
            return simplejson.dumps({'html':rendered})

dajaxice_functions.register(save_items)