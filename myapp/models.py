import uuid
from datetime import datetime
from datetime import date
from django.db import models
from django.contrib.auth.models import User

# defining the Roles of the Staff Users
ROLES_CHOICES = (
	('Admin', 'Admin'),
	('Police', 'Police'),
	('BRTA_Staff', 'BRTA_Staff'),
	)



# Extending User Profile
class UserProfile(models.Model):
	user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
	role = models.CharField(max_length=20, choices=ROLES_CHOICES)
	designation = models.CharField(max_length=60,null=True, blank=True)

	def __str__(self):
		return str(self.role)


# Registered Owner Table in the Database
class registered_vehicle_owner_table(models.Model):
	registered_vehicle_owner = models.CharField(max_length=30, null=False, blank=False)
	registered_owner_id = models.UUIDField(primary_key=True,default = uuid.uuid4, editable = False)
	registered_owner_address = models.CharField(max_length=160)
	registered_owner_dob = models.DateField()
	registered_owner_data_create = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return str(self.registered_vehicle_owner)+' - '+str(self.registered_owner_id)

# Registered Vehicle Table in the Database
class vehicle_license_plate_registration_table(models.Model):
	city_name = models.CharField(max_length=30, null=False, blank=False)
	vehicle_classification = models.CharField(max_length=10, null=False, blank=False)
	vin = models.CharField(max_length=10, primary_key=True,null=False, blank=False)
	engine_cc = models.IntegerField()
	vehicle_brand = models.CharField(max_length=30)
	registered_owner_id = models.ForeignKey(registered_vehicle_owner_table, on_delete=models.CASCADE)

	def __str__(self):
		return str(self.vin)

class FelonyList(models.Model):
	felony_name = models.CharField(max_length=60)
	felony_charge = models.IntegerField()
	felony_details = models.CharField(max_length=200, null=True, blank=True)

	def __str__(self):
		return str(self.felony_name)

class IncidentVehicular(models.Model):
	incident_id = models.UUIDField(primary_key=True, default = uuid.uuid4, editable = False)
	incident_title = models.CharField(max_length=100)
	felony = models.ManyToManyField(FelonyList)
	registered_owner_id = models.ForeignKey(registered_vehicle_owner_table, on_delete=models.CASCADE)
	vin = models.ForeignKey(vehicle_license_plate_registration_table, on_delete=models.CASCADE)
	submition_date = models.DateTimeField(auto_now_add=True)
	submitted_by = models.ForeignKey(User, on_delete=models.CASCADE)
