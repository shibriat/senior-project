# Generated by Django 4.1.5 on 2023-01-27 12:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('myapp', '0013_remove_vehicleownerfelonyincident_incident_charges_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='FelonyList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('felony_name', models.CharField(max_length=60)),
                ('felony_charge', models.IntegerField()),
                ('felony_details', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='IncidentVehicular',
            fields=[
                ('incident_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('incident_title', models.CharField(max_length=100)),
                ('submition_date', models.DateTimeField(auto_now_add=True)),
                ('felony', models.ManyToManyField(to='myapp.felonylist')),
                ('registered_owner_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.registered_vehicle_owner_table')),
                ('submitted_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('vin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.vehicle_license_plate_registration_table')),
            ],
        ),
    ]
