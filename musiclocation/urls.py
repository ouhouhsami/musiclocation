from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from django.contrib import admin
admin.autodiscover()

from dajaxice.core import dajaxice_autodiscover
dajaxice_autodiscover()
from django.conf import settings


urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'musiclocation.views.home', name='home'),
    ('^channel.html$', TemplateView.as_view(template_name='channel.html')),
    url(r'^accounts/logout/$', 'musiclocation.views.logout_view', name='logout'),
    (r'^dajaxice/', include('dajaxice.urls')),
    url(r'', include('social_auth.urls')),
    # url(r'^musiclocation/', include('musiclocation.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
