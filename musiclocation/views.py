import datetime
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.forms.models import inlineformset_factory
from utils.models import ItemLocation
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.models import User
from utils.forms import ItemLocationForm


def home(request):
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
                           {'formset':formset },
                          context_instance=RequestContext(request))

def logout_view(request):
    logout(request)
    return redirect('home')
    