# coding=utf-8

from django.forms import ModelForm, HiddenInput, TextInput, BooleanField
from utils.models import ItemLocation
from urllib2 import urlopen
from django.utils import simplejson
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from pprint import pprint

class ItemLocationForm(ModelForm):
    """
    ItemLocation model form
    """
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Div(
            Div('DELETE', style="display:none;"), Field('position'),Field('item_id'),Field('item_type'), css_class="well", style="padding: 5px; margin-bottom: 5px;"
        )        
        super(ItemLocationForm, self).__init__(*args, **kwargs)
        a = list(self.helper.layout.fields)
        if self.instance.item_id is not None and self.instance.item_type is not None:
            # get deezer information
            url = 'http://api.deezer.com/2.0/%s/%s' % (self.instance.item_type, self.instance.item_id)
            data = simplejson.load(urlopen(url))
            if self.instance.item_type == 'track':
                try:
                    label = "<span class='item_label'><i>%s</i> (%s)</span> %s" % (data['title'], data['album']['title'], data['artist']['name'])
                    # return to tuple not mandatory
                except:
                    label = "<span class='item_label'><i>connections quota exceeded</i> reload !</span>" 
        else:
             label = "<span class='item_label'></span>"          
        #a.insert(0, HTML(u'<i class="icon-map-marker drag" title="click to center map on this track"></i> <i class="icon-play" title="click to play track"></i> %s <a class="close" >×</a>' % (label)))
        a.insert(0, HTML(u'<i class="icon-map-marker" title="click to center map on this track"></i> <i class="icon-play" title="click to play track"></i> %s <a class="close" >×</a>' % (label)))
        self.helper.layout.fields = tuple(a)

    class Meta:
        model = ItemLocation
        exclude = ('user', )
        widgets = {'position':HiddenInput(attrs={'class':'marker'}), 
                   'item_id':HiddenInput(),'item_type':HiddenInput(),}

