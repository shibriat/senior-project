import uuid
from datetime import datetime
from datetime import date
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

# Data table of Customized User Model of the System
class User(AbstractUser):
	# defining the Roles of the Staff Users
	ROLES_CHOICES = (
		('Admin', 'Admin'),
		('Police', 'Police'),
		('BRTA_Staff', 'BRTA_Staff'),
	)
	role = models.CharField(max_length=30, choices=ROLES_CHOICES)
	phone = models.CharField(max_length=15, null=True, blank=True)
# Registered Owner Table in the Database
class RegisteredVehicleOwner(models.Model):
	registered_vehicle_owner = models.CharField(max_length=30, null=False, blank=False)
	registered_owner_id = models.UUIDField(primary_key=True,default = uuid.uuid4, editable = False)
	registered_owner_email = models.EmailField(max_length=255, null=False, blank=False)
	registered_owner_address = models.CharField(max_length=160)
	registered_owner_dob = models.DateField()
	registered_owner_data_create = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return str(self.registered_vehicle_owner)+' - '+str(self.registered_owner_id)

# Registered Vehicle Table in the Database
class RegisteredVehicle(models.Model):
	city_name = models.CharField(max_length=30, null=False, blank=False)
	vehicle_classification = models.CharField(max_length=10, null=False, blank=False)
	vin = models.CharField(max_length=10, primary_key=True,null=False, blank=False)
	engine_cc = models.IntegerField()
	vehicle_brand = models.CharField(max_length=30)
	registered_owner_id = models.ForeignKey(RegisteredVehicleOwner, on_delete=models.CASCADE)

	def __str__(self):
		return str(self.vin)
# Felony Table in the Database
class FelonyList(models.Model):
	felony_name = models.CharField(max_length=60)
	felony_charge = models.IntegerField()
	felony_details = models.CharField(max_length=200, null=True, blank=True)

	def __str__(self):
		return str(self.felony_name)
# Incident Table in the Database
class IncidentVehicular(models.Model):
	incident_id = models.UUIDField(primary_key=True, default = uuid.uuid4, editable = False)
	incident_title = models.CharField(max_length=100)
	felony = models.ManyToManyField(FelonyList)
	registered_owner_id = models.ForeignKey(RegisteredVehicleOwner, on_delete=models.CASCADE)
	vin = models.ForeignKey(RegisteredVehicle, on_delete=models.CASCADE)
	submition_date = models.DateTimeField(auto_now_add=True)
	submitted_by = models.ForeignKey(User, on_delete=models.CASCADE)
