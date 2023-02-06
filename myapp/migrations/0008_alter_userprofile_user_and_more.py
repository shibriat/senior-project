# Generated by Django 4.1.5 on 2023-01-26 17:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('myapp', '0007_vehicleownerfelonyincident_incident_submition_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='vehicleownerfelonyincident',
            name='incident_details',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
