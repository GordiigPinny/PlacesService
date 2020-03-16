from django.contrib import admin
from Places.models import Place, Accept, Rating, PlaceImage


admin.site.register(Place)
admin.site.register(Accept)
admin.site.register(Rating)
admin.site.register(PlaceImage)
