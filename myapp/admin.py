from django.contrib import admin
from .models import UserProfile, registered_vehicle_owner_table, vehicle_license_plate_registration_table, FelonyList, IncidentVehicular

admin.site.register(UserProfile)
admin.site.register(registered_vehicle_owner_table)
admin.site.register(vehicle_license_plate_registration_table)
admin.site.register(FelonyList)
admin.site.register(IncidentVehicular)