from django.contrib import admin
from utils.models import ItemLocation

class ItemLocationAdmin(admin.ModelAdmin):
    pass
admin.site.register(ItemLocation, ItemLocationAdmin)