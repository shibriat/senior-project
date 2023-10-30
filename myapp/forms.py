from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import *
from django import forms
from django.forms import ModelForm

class CreateUserForm(UserCreationForm):
	class Meta:
		model = User
		fields = ('username', 'email', 'role', 'is_staff', 'password1', 'password2')

		labels = {
            'username': 'Username',
            'email': 'Email',
            'role': 'Role',
            'is_staff': 'Is Staff',
            'password1': 'Password',
            'password2': 'Confirm Password',
        }

		widgets = {
			'username': forms.TextInput(attrs={
				'class': 'form-control',
				'Placeholder': 'Username',
				}),
			'email': forms.EmailInput(attrs={
				'class': 'form-control',
				'Placeholder': 'Email',
				}),
			'is_staff': forms.CheckboxInput(
				attrs={
					'class': '',

				}
				),
			'role': forms.Select(attrs={
				'class': 'form-control',
				'Placeholder': 'Role',
				}),
			'password1': forms.PasswordInput(attrs={
				'class': 'form-control',
				'Placeholder': 'Password',
				}),
			'password2': forms.PasswordInput(attrs={
				'class': 'form-control',
				'Placeholder': 'Confirm Password',
				})
		}


	def __init__(self, *args, **kwargs):
		super(CreateUserForm, self).__init__(*args, **kwargs)

		self.fields['password1'].widget.attrs['class'] = 'form-control'
		self.fields['password1'].widget.attrs['placeholder'] = 'Password'
		self.fields['password2'].widget.attrs['class'] = 'form-control'
		self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'

class VehicleOwnerForm(ModelForm):
	class Meta:
		model = RegisteredVehicleOwner
		fields = (	'registered_vehicle_owner',
					'registered_owner_email',
					'registered_owner_address',
					'registered_owner_dob')
		labels = {
			'registered_vehicle_owner': 'Registered Vehicle Owner',
			'registered_owner_email': 'Email Address',
			'registered_owner_address': "Registered Owner's Address",
			'registered_owner_dob': 'DOB'
		}

		widgets = {
			'registered_vehicle_owner': forms.TextInput(
				attrs={
					'class': 'form-control',
					'Placeholder': 'Vehicle Owner',
				}),
			'registered_owner_email': forms.EmailInput(
				attrs={
					'class': 'form-control',
					'Placeholder': 'Email Address',
				}),
			'registered_owner_address': forms.TextInput(
				attrs={
					'class': 'form-control',
					'Placeholder': 'Owner Address',
				}),
			'registered_owner_dob': forms.DateInput(
				attrs={
					'class': 'form-control',
					'Placeholder': 'YYYY-MM-DD'
				}
				)
		}

class VehicleRegistrationForm(ModelForm):
	class Meta:
		model = RegisteredVehicle
		fields = (	'city_name',
					'vehicle_classification',
					'vin',
					'engine_cc',
					'vehicle_brand',
					'registered_owner_id')

		labels = {
			'city_name': 'City',
			'vehicle_classification': 'Vehicle Classification',
			'vin': 'Vin',
			'engine_cc': 'Engin CC',
			'vehicle_brand': 'Vehicle Brand',
			'registered_owner_id': '',
		}

		widgets = {
			'city_name': forms.TextInput(
				attrs={
					'class': 'form-control',
					'Placeholder': 'City Name',
				}),
			'vehicle_classification': forms.TextInput(
				attrs={
					'class': 'form-control',
					'Placeholder': 'Vehicle Classification',
				}
				),
			'vin': forms.TextInput(
				attrs={
					'class': 'form-control',
					'Placeholder': 'VIN',
				}),
			'engine_cc': forms.NumberInput(
				attrs={
					'class': 'form-control disabled',
					'Placeholder': 'Engine CC',
				}),
			'vehicle_brand': forms.TextInput(
				attrs={
					'class': 'form-control',
					'Placeholder': 'Vehicle Brand',
				}),
			'registered_owner_id': forms.Select(
				attrs={
					'class': 'form-control',
					'Value': 'Select Owner',
				}
				)
		}

# ADD UPDATE DELETE READ Felony 
class FelonyForm(ModelForm):
	class Meta:
		model = FelonyList
		fields = '__all__'

#ADD UPDATE DELETE READ Incident
class IncidentForm(ModelForm):
	class Meta:
		model = IncidentVehicular
		fields = (
			'incident_title',
			'felony',
			'registered_owner_id',
			'vin',
			'submitted_by',
			)
		labels = {
			'incident_title':'',
			'felony':'',
			'registered_owner_id': '',
			'vin': '',
			'submitted_by': '',
		}

		widgets = {
			'incident_title': forms.TextInput(
				attrs={
					'class': 'form-control',
					'Placeholder': 'Incident Title',
				}),
			'felony': forms.SelectMultiple(
				attrs={
					'class': 'form-control',
					'Placeholder': 'Select Felony(s)',
				}),
			'registered_owner_id': forms.Select(
				attrs={
					'class': 'form-control',
					'Placeholder': '',
				}),
			'vin': forms.Select(
				attrs={
					'class': 'form-control',
				})
			
		}