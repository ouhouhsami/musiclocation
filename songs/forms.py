# coding=utf-8

from django.forms import ModelForm, HiddenInput, TextInput, BooleanField
from songs.models import SongLocation
from urllib2 import urlopen
from django.utils import simplejson
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from fields import TrackIdInput
from django import forms

class SongLocationForm(ModelForm):
    """
    SongLocation model form
    """
    item_id = forms.IntegerField(widget=TrackIdInput())
    class Meta:
        model = SongLocation
        exclude = ('user', 'json' )
        widgets = {'position':HiddenInput(), }
        #           'item_id':HiddenInput(),'item_type':HiddenInput(),}

