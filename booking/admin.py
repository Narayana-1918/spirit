from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(TourPackage)
class TourPackageAdmin(admin.ModelAdmin):
    # Automatically show all fields in the admin form
    pass
    # fields = [field.name for field in TourPackage._meta.fields]

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    # Automatically show all fields in the admin form
    pass
    # fields = [field.name for field in Destination._meta.fields]

@admin.register(Places)
class PlacesAdmin(admin.ModelAdmin):
    # Automatically show all fields in the admin form
    # fields = [field.name for field in Places._meta.fields]
    pass


@admin.register(PackageItinerary)
class PackageItineraryAdmin(admin.ModelAdmin):
    # Automatically show all fields in the admin form
    # fields = [field.name for field in PackageItinerary._meta.fields]
    pass


@admin.register(DestinationItinerary)
class DestinationItineraryAdmin(admin.ModelAdmin):
    # Automatically show all fields in the admin form
    # fields = [field.name for field in DestinationItinerary._meta.fields]
    pass