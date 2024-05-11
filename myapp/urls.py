from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
	path('', views.display_home_page, name='home'),
	path('login/', views.login_user, name='login'),
	path('logout/', views.logout_user, name='logout'),
	path('register/', views.register_user, name='register'),
	path('manage-user/', views.manage_user, name='manage-user'),
	path('update-user/<str:user_id>', views.update_user, name='update-user'),
	path('delete-user/<str:user_id>', views.delete_user, name='delete-user'),

	path('search/', views.search_item, name='search'),

	path('register-user/', views.register_owner, name='register-user'),
	path('register-vehicle/<str:owner_id>', views.register_vehicle,name='register-vehicle'),
	path('display-database/', views.display_database, name='display-database'),

	path('update-vehicle-owner/<str:owner_id>', views.update_owner, name='update-vehicle-owner'),
	path('delete-vehicle-owner/<str:owner_id>', views.delete_owner, name='delete-vehicle-owner'),
	path('details/<str:owner_id>', views.generate_owner_details, name='details'),

	path('update-vehicle/<str:vin>', views.update_vehicle, name='update-vehicle'),
	path('delete-vehicle/<str:vin>', views.delete_vehicle, name='delete-vehicle'),

	path('checkplate/realtime/', views.checkplate_realtime, name='checkplate-realtime'),
	path('checkplate/readpicture/', views.checkplate_picture, name='readpicture'),


	path('display-owner/<str:owner_id>', views.display_owner, name='display-owner'),
	path('display-vehicle/<str:vin>', views.display_vehicle, name='display-vehicle'),

	path('register-incident/<str:vin>/', views.register_incident, name='register-incident'),
	path('run-vin/', views.run_vin, name='run-vin'),

	path('report/<str:incident_id>', views.display_incident, name='report'),
	path('generate-incident/<str:incident_id>', views.generate_incident, name='generate-incident'),
	path('generate-bill/<str:incident_id>', views.generate_bill, name='generate-bill'),
	path('generate-details/<str:owner_id>', views.generate_vehicle_owner_details, name='generate-details'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)