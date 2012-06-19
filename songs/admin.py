from django.contrib import admin
from songs.models import SongLocation

class SongLocationAdmin(admin.ModelAdmin):
    pass
admin.site.register(SongLocation, SongLocationAdmin)