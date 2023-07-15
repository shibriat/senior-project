from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Assigning Field list in 'fields' variable
fields = list(UserAdmin.fieldsets)
# Serializing these fields in the fields[1] index of list fields
fields[1] = ('Personal Info', { 'fields': ('first_name',  'last_name', 'email', 'phone', 'role')})
# Storing fields list as tuple in UserAdmin fieldsets
UserAdmin.fieldsets = tuple(fields)
# Registering User_T in the AdminPanel
admin.site.register(User, UserAdmin)

admin.site.register(RegisteredVehicleOwner)
admin.site.register(RegisteredVehicle)
admin.site.register(FelonyList)
admin.site.register(IncidentVehicular)