from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import CreateUserForm, UserProfileForm, VehicleOwnerForm, VehicleRegistrationForm, IncidentForm
from .models import UserProfile, registered_vehicle_owner_table, vehicle_license_plate_registration_table, IncidentVehicular


from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
import base64

import torch
from easyocr import Reader
import re

import cv2
import numpy as np

from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, A4

import smtplib
import ssl
from email.message import EmailMessage


def checkuserrole(request):
    profile = UserProfile.objects.filter(user__pk=request.user.id)
    if profile[0].role == 'Admin':
        return profile[0].role
    if profile[0].role == 'BRTA_Staff':
        return profile[0].role

    if profile[0].role == 'Police':
        return profile[0].role
    else:
        return redirect('login')


def get_vin(frame):

    # Defining dictionary to translate bangla numbers to english number
    dic = {
        '০': '0',
        '১': '1',
        '২': '2',
        '৩': '3',
        '৪': '4',
        '৫': '5',
        '৬': '6',
        '৭': '7',
        '৮': '8',
        '৯': '9'
    }

    reader = Reader(['bn'], gpu=True)
    results = reader.readtext(frame)

    text = ''
    for result in results:
        text = text + result[1]

    texts = re.findall("[০১২৩৪৫৬৭৮৯]*", text)
    del text
    vins = ''
    for text in texts:
        if text is not None:
            vins = vins + text

    vin = ''
    for text in vins:
        vin = vin + str(dic[text])
    del vins
    return str(vin)


# Mail the notification to the users
def sendmail(request, subject, message, email_receiver):
    if request.user.is_authenticated:
        if checkuserrole(request) == 'Police' or checkuserrole(request) == 'Admin':
            email_sender = 'smarifmahmud9@gmail.com'
            email_password = 'nvchliisoaxrqorw'

            body = f"""
			{message}
			"""

            email = EmailMessage()
            email['From'] = email_sender
            email['To'] = email_receiver
            email['Subject'] = subject
            email.set_content(body)

            context = ssl.create_default_context()

            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(email_sender, email_password)
                smtp.sendmail(email_sender, email_receiver, email.as_string())
            return 'email sent'
        else:
            return redirect('home')
    else:
        return redirect('login')

# Create your views here.


def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            user = authenticate(
                request, username=request.POST['username'], password=request.POST['password'])
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.add_message(request, messages.INFO,
                                     'Wrong username or password')
                return redirect('login')
        return render(request, 'login/login.html', {})


def logout_user(request):
    logout(request)
    return redirect('login')


def display_home_page(request):
    if request.user.is_authenticated:
        if checkuserrole(request) == 'Admin':
            return render(request, 'home/home.html', {'role': checkuserrole(request)})

        if checkuserrole(request) == 'BRTA_Staff':
            return render(request, 'home/home.html', {'role': checkuserrole(request)})

        if checkuserrole(request) == 'Police':
            return render(request, 'home/home.html', {'role': checkuserrole(request)})
    else:
        return redirect('login')


def register_user(request):
    if request.user.is_authenticated:
        if checkuserrole(request) == 'Admin':
            form = CreateUserForm()
            if request.method == "POST":
                form = CreateUserForm(request.POST)
                if form.is_valid():
                    form.save()
                    messages.add_message(
                        request, messages.SUCCESS, 'User Registered Successfully')
                else:
                    messages.add_message(request, messages.INFO, 'Error')

            return render(request, 'register/register.html', {
                'form': form,
                'role': checkuserrole(request),
            })
        else:
            return redirect('home')

    else:
        return redirect('login')


def manage_user(request):
    if request.user.is_authenticated:
        if checkuserrole(request) == 'Admin':
            users = User.objects.all()
            return render(request, 'manage/manage_user.html', {'users': users, 'role': checkuserrole(request), })
        else:
            return redirect('home')

    else:
        return redirect('login')


def manage_user_role(request, userid):
    if request.user.is_authenticated:
        if checkuserrole(request) == 'Admin':
            data = UserProfile.objects.filter(user__pk=userid)
            form = UserProfileForm(request.POST or None, instance=data[0])
            if form.is_valid():
                instances = form.save()
                messages.add_message(
                    request, messages.SUCCESS, 'User Role Updated')
                user = User.objects.get(pk=userid)

                sendmail(request, 'User Role Update', f"""
					Dear {user.username}, 
					your role has been updated to {instances.role}, 

					Regards 
					{request.user}""", user.email)
            return render(request, 'manage/manage_user_role.html', {'data': data,
                                                                    'form': form,
                                                                    'role': checkuserrole(request),
                                                                    })
        else:
            return redirect('home')
    else:
        return redirect('login')


def update_user(request, user_id):
    if request.user.is_authenticated:
        if checkuserrole(request) == 'Admin':
            USER = User.objects.get(pk=user_id)
            form = CreateUserForm(request.POST or None, instance=USER)
            if form.is_valid():
                instances = form.save()
                messages.add_message(
                    request, messages.SUCCESS, 'User Information Updated in the Database')

                sendmail(request, f'User Profile Update of {USER.username}', f"""
					Dear {request.POST['username']},
					Your Updated Credentials:
					USERNAME: {request.POST['username']}
					PASSWORD: {request.POST['password2']}
					""", request.POST['email'])
            return render(request, 'manage/update_user.html', {
                'form': form,
                'userid': user_id,
                'role': checkuserrole(request),
            })
        else:
            return redirect('home')

    else:
        return redirect('login')


def delete_user(request, user_id):
    if request.user.is_authenticated:
        if checkuserrole(request) == 'Admin':
            USER = User.objects.get(pk=user_id)
            if USER:
                USER.delete()
                messages.add_message(
                    request, messages.SUCCESS, 'User Removed From the Database')
                return redirect('manage-user')
            else:
                return redirect('home')
        else:
            return redirect('home')
    else:
        return redirect('login')


########################################################### BRTA OPERATIONS ###########################################################

def register_owner(request):
    if request.user.is_authenticated:
        if checkuserrole(request) == 'BRTA_Staff' or checkuserrole(request) == 'Admin':
            form = VehicleOwnerForm()
            if request.method == 'POST':
                form = VehicleOwnerForm(request.POST)
                if form.is_valid():
                    form.save()
                    messages.add_message(
                        request, messages.SUCCESS, 'Owner Registered in the Database')
                    try:
                        sendmail(request, f"Vehicle Owner Registration of {request.POST['registered_vehicle_owner']}", f"""
						Dear {request.POST['registered_vehicle_owner']},
						Your profile has been Successfully registered into the System

						Regards,
						License Plate Tracking System
						""", request.POST['registered_owner_email'])
                    except:
                        pass
                    return redirect('display-database')
                else:
                    messages.add_message(
                        request, messages.INFO, 'Encoutered Error while Registering Owner')
            return render(request, '1_brta_site/register_owner.html', {'form': form,
                                                                       'role': checkuserrole(request), })
        else:
            return redirect('home')
    else:
        return redirect('login')


def register_vehicle(request, owner_id):
    if request.user.is_authenticated:
        if checkuserrole(request) == 'BRTA_Staff' or checkuserrole(request) == 'Admin':
            form = VehicleRegistrationForm()
            indivs = registered_vehicle_owner_table.objects.get(pk=owner_id)
            if request.method == 'POST':
                form = VehicleRegistrationForm(request.POST)
                if form.is_valid():
                    form.save()
                    messages.add_message(
                        request, messages.SUCCESS, 'Registered a vehicle on The Following Owner')

                    try:
                        sendmail(request, f"Successfully Registered Vehicle, VIN: {request.POST['vin']} to {indivs.registered_vehicle_owner}", f"""
						Congratilations {indivs.registered_vehicle_owner},
						The vehicle with following Cedentials and Identifications
						City name: {request.POST['city_name']}, Classification: {request.POST['vehicle_classification']}, VIN: {request.POST['vin']}
						Model: {request.POST['vehicle_brand']}, Engine CC: {request.POST['engine_cc']}
						Has successfully been registered to "{indivs.registered_vehicle_owner}"

						Regards,
						License Plate Tracking System
						""", indivs.registered_owner_email)
                    except:
                        pass

                    return redirect('display-database')
            return render(request, '1_brta_site/register_vehicle.html', {'form': form, 'indivs': indivs, 'role': checkuserrole(request), })
        else:
            return redirect('home')
    else:
        return redirect('login')


def display_database(request):
    if request.user.is_authenticated:
        if checkuserrole(request) == 'BRTA_Staff' or checkuserrole(request) == 'Admin':
            indivs = registered_vehicle_owner_table.objects.all()
            vins = vehicle_license_plate_registration_table.objects.all()

            ownerForm = VehicleOwnerForm()
            vehicleForm = VehicleRegistrationForm()
            if request.method == 'POST':
                ownerForm = VehicleOwnerForm(request.POST)
                vehicleForm = VehicleRegistrationForm(request.POST)
                if ownerForm.is_valid() & vehicleForm.is_valid():
                    ownerForm.save()
                    vehicleForm.save()
                    messages.add_message(
                        request, messages.SUCCESS, 'Data Stored')
                    return redirect('display-database')
                else:
                    messages.add_message(
                        request, messages.INFO, 'Error Found While Storing Data')
                    return redirect('display-database')
            return render(request, '1_brta_site/display_data_base.html', {
                'indivs': indivs,
                'vins': vins,
                'ownerForm': ownerForm,
                'vehicleForm': vehicleForm,
                'role': checkuserrole(request),
            })
        else:
            return redirect('home')
    else:
        return redirect('login')

# UPDATE AND DELETE VEHICLE OWNER


def update_owner(request, owner_id):
    if request.user.is_authenticated:
        if checkuserrole(request) == 'BRTA_Staff' or checkuserrole(request) == 'Admin':
            vehicle = vehicle_license_plate_registration_table.objects.filter(
                registered_owner_id__pk=owner_id)
            indiv = registered_vehicle_owner_table.objects.get(pk=owner_id)
            form = VehicleOwnerForm(request.POST or None, instance=indiv)
            if form.is_valid():
                form.save()
                messages.add_message(
                    request, messages.SUCCESS, 'Vehicle Owner Information Updated in the Database')
                try:
                    sendmail(request, f"Successfully Updated Registered Owner {request.POST['registered_vehicle_owner']}'s Profile", f"""
					Dear {request.POST['registered_vehicle_owner']},
					Your Credentials has been updated

					Regards,
					License Plate Tracking System
					""", request.POST['registered_owner_email'])
                except:
                    pass
            return render(request, '1_brta_site/manage_person.html', {'form': form, 'owner_id': owner_id, 'indiv': indiv, 'vehicle': vehicle, 'role': checkuserrole(request), })
        else:
            return redirect('home')
    else:
        return redirect('login')


def delete_owner(request, owner_id):
    if request.user.is_authenticated:
        if checkuserrole(request) == 'BRTA_Staff' or checkuserrole(request) == 'Admin':
            indiv = registered_vehicle_owner_table.objects.get(pk=owner_id)
            if indiv:
                indiv.delete()
                return redirect('display-database')
            else:
                return redirect('home')
        else:
            return redirect('home')
    else:
        return redirect('login')

###

# UPDATE AND DELETE VEHICLE


def update_vehicle(request, vin):
    if request.user.is_authenticated:
        if checkuserrole(request) == 'BRTA_Staff' or checkuserrole(request) == 'Admin':
            vehicle = vehicle_license_plate_registration_table.objects.get(
                pk=vin)
            form = VehicleRegistrationForm(
                request.POST or None, instance=vehicle)
            if form.is_valid():
                form.save()
                messages.add_message(
                    request, messages.SUCCESS, 'Vehicle Registration Information Updated in the Database')
                try:
                    sendmail(request, f"Details of Vehicle {request.POST['vin']} has been Updated",
                             f"""
					Dear {registered_vehicle_owner_table.objects.get(pk=vehicle.registered_owner_id.registered_owner_id).registered_vehicle_owner},
					Your details of the vehicle with following information City name: {request.POST['city_name']}, Classification: {request.POST['vehicle_classification']}, VIN: {request.POST['vin']}
					Model: {request.POST['vehicle_brand']}, Engine CC: {request.POST['engine_cc']}
					has been updated 

					Regards,
					License Plate Tracking System
					""", registered_vehicle_owner_table.objects.get(pk=vehicle.registered_owner_id.registered_owner_id).registered_owner_email)
                except:
                    pass
            return render(request, '1_brta_site/manage_vehicle.html', {'form': form, 'vin': vin, 'vehicle': vehicle, 'role': checkuserrole(request), })
        else:
            return redirect('home')
    else:
        return redirect('login')


def delete_vehicle(request, vin):
    if request.user.is_authenticated:
        if checkuserrole(request) == 'BRTA_Staff' or checkuserrole(request) == 'Admin':
            vehicle = vehicle_license_plate_registration_table.objects.get(
                pk=vin)
            if vehicle:
                vehicle.delete()
                return redirect('display-database')
            else:
                return redirect('home')
        else:
            return redirect('home')
    else:
        return redirect('login')

# Print Vehicle owner details for BRTA Staff users


def generate_owner_details(request, owner_id):
    if request.user.is_authenticated:
        if checkuserrole(request) == 'BRTA_Staff' or checkuserrole(request) == 'Admin':
            # Create Bytestream Buffer
            buffer = io.BytesIO()
            canv = canvas.Canvas(buffer, pagesize=A4, bottomup=0)
            # Create text object
            textobj = canv.beginText()
            textobj.setTextOrigin(inch, inch)
            textobj.setFont('Times-Roman', 10)

            # Get object of that owner id
            owner = registered_vehicle_owner_table.objects.get(pk=owner_id)
            # Create Empty List of lines
            lines = []
            # Append the data in the list of lines
            lines.append(
                f"Detailed Report on {owner.registered_vehicle_owner}")
            lines.append(
                '_________________________________________________________________________________________')
            lines.append("Registered Owner's details")
            lines.append(
                '_________________________________________________________________________________________')
            lines.append(
                f'Registered Vehicle Owner: {owner.registered_vehicle_owner}')
            lines.append(
                f'registered Vehicle Owner ID: {owner.registered_owner_id}')
            lines.append(
                f"Registered Owner's Address: {owner.registered_owner_address}")
            lines.append(
                f"Registered Vehicle Owner's DOB: {owner.registered_owner_dob}")
            lines.append(
                f"Registration Date: {owner.registered_owner_data_create}")
            lines.append('')
            lines.append(
                '_________________________________________________________________________________________')
            lines.append(f"Registered Owned Vehicle(s)")
            lines.append(
                '_________________________________________________________________________________________')

            vehicles = vehicle_license_plate_registration_table.objects.filter(
                registered_owner_id__pk=owner_id)

            if vehicles:
                for vehicle in vehicles:
                    lines.append(f"City Name: {vehicle.city_name}")
                    lines.append(
                        f"Vehicle Classification: {vehicle.vehicle_classification}")
                    lines.append(f"VIN: {vehicle.vin}")
                    lines.append(f"Engine CC: {vehicle.engine_cc}")
                    lines.append(f"Vehicle Brand: {vehicle.vehicle_brand}")
                    lines.append(
                        f"Vehicle Registered To: {vehicle.registered_owner_id.registered_vehicle_owner}")
                    lines.append('')
                lines.append(
                    '_________________________________________________________________________________________')
            else:
                lines.append(
                    f"{owner.registered_vehicle_owner} has no Registered Vehicle(s)")
                lines.append(
                    '_________________________________________________________________________________________')
            lines.append(f"Printed by {request.user}")
            # Putting lines in text object
            for line in lines:
                textobj.textLine(line)
            # Finishing Up file by generating
            canv.drawText(textobj)
            canv.showPage()
            canv.save()
            buffer.seek(0)

            # Return the generated pdf file
            return FileResponse(buffer, as_attachment=True, filename=f'{owner_id}.pdf')
        else:
            return redirect('home')
    else:
        return redirect('login')
############################################

# SEARCH ITEM


def search_item(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            searched = request.POST['searched']
            results_vehicle = vehicle_license_plate_registration_table.objects.filter(
                Q(vin__contains=searched) |
                Q(city_name__contains=searched) |
                Q(vehicle_classification__contains=searched) |
                Q(vehicle_brand__contains=searched)
            )

            results_owner = registered_vehicle_owner_table.objects.filter(
                Q(registered_owner_id__contains=searched) |
                Q(registered_vehicle_owner__contains=searched)
            )

            return render(request, 'searched/searched.html', {'searched': searched, 'results': results_vehicle, 'results_owner': results_owner, 'role': checkuserrole(request), })
        else:
            return redirect('home')
    else:
        return redirect('login')


# POLICE

def checkplate_realtime(request):
    if request.user.is_authenticated:
        if checkuserrole(request) == 'Police' or checkuserrole(request) == 'Admin':
            if request.method == 'POST':
                frame_data = request.POST['frame_data']
                video_frame = ''
                if frame_data:
                    # Convert frame_data from base64 to numpy array
                    frame_data = frame_data.split(',')[1]
                    nparr = np.frombuffer(
                        base64.b64decode(frame_data), np.uint8)
                    # Convert numpy array to video frame
                    video_frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                vin = get_vin(video_frame)
                try:
                    vehicle = vehicle_license_plate_registration_table.objects.get(
                        pk=vin)
                    felonys = IncidentVehicular.objects.filter(vin__pk=vin)
                except:
                    vehicle = None
                    felonys = None
                return render(request, '1_police_site/check_realtime.html', {'vin': vin, 'vehicle': vehicle, 'felonys': felonys, 'role': checkuserrole(request), })
            return render(request, '1_police_site/check_realtime.html', {'role': checkuserrole(request), })
        else:
            return redirect('home')
    else:
        return redirect('login')


def checkplate_picture(request):
    if request.user.is_authenticated:
        if checkuserrole(request) == 'Police' or checkuserrole(request) == 'Admin':
            if request.method == 'POST':
                try:
                    image = request.FILES.get('image')
                    print('image type: ', image)
                    image = cv2.imdecode(np.fromstring(
                        image.read(), np.uint8), cv2.IMREAD_UNCHANGED)

                    # Convert the image to a video frame
                    frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                    vin = get_vin(frame)

                    try:
                        vehicle = vehicle_license_plate_registration_table.objects.get(
                            pk=vin)
                        felonys = IncidentVehicular.objects.filter(vin__pk=vin)
                    except:
                        vehicle = None
                        felonys = None
                    return render(request, '1_police_site/read_picture.html', {'vin': vin,
                                                                               'vehicle': vehicle,
                                                                               'felonys': felonys,
                                                                               'role': checkuserrole(request), })
                except:
                    try:
                        print('touched\n')
                        return render(request, '1_police_site/read_picture.html', {'role': checkuserrole(request), })
                    except:
                        pass
            return render(request, '1_police_site/read_picture.html', {'role': checkuserrole(request), })
        else:
            return redirect('home')
    else:
        return redirect('login')


def register_incident(request, vin):
    if request.user.is_authenticated:
        if checkuserrole(request) == 'Police' or checkuserrole(request) == 'Admin':
            form = IncidentForm()
            if request.method == 'POST':
                form = IncidentForm(request.POST)
                if form.is_valid():
                    instance = form.save()
                    messages.add_message(
                        request, messages.SUCCESS, 'Incident Registered Successfully')
                    vehicle = vehicle_license_plate_registration_table.objects.get(
                        pk=vin)
                    felonys = IncidentVehicular.objects.filter(vin__pk=vin)

                    charge = ''
                    for felony in instance.felony.all():
                        charge = charge + str(felony.felony_name) + ' | '

                    del felony
                    try:
                        sendmail(request, f"Case ID:{instance.incident_id}",
                                 f"""
						Dear {instance.registered_owner_id.registered_vehicle_owner},
						You have been registered Case on following charge(s): {str(charge)} on Vehicle VIN: {instance.vin}
						Pay the Fine on any branch of "Sonali Bank" by the due date to avoid Extra late Charge.

						============================================================================================================================
						Case Title: {instance.incident_title}
						Case ID: {instance.incident_id}
						Committed Felony(ies): {charge}
						Registered Vehicle Owner: {instance.registered_owner_id.registered_vehicle_owner}
						Vehicle Identification Number: {instance.vin}
						Case Registration Date: {instance.submition_date}
						Case Registered By: {instance.submitted_by}
						============================================================================================================================

						Regards,
						License Plate Tracking System
						""", instance.registered_owner_id.registered_owner_email)
                    except:
                        pass
                    return render(request, '1_police_site/display_vehicle.html', {'vin': vin, 'vehicle': vehicle, 'felonys': felonys, 'role': checkuserrole(request), })
            vehicle = vehicle_license_plate_registration_table.objects.get(
                pk=vin)
            return render(request, '1_police_site/register_incident.html', {'role': checkuserrole(request),
                                                                            'form': form,
                                                                            'vehicle': vehicle,
                                                                            })
        else:
            return redirect('home')
    else:
        return redirect('login')


def run_vin(request):
    if request.user.is_authenticated:
        if checkuserrole(request) == 'Police' or checkuserrole(request) == 'Admin':
            if request.method == 'POST':
                try:
                    vehicle = vehicle_license_plate_registration_table.objects.get(
                        pk=request.POST['searched'])
                    felonys = IncidentVehicular.objects.filter(
                        vin__pk=request.POST['searched'])
                except:
                    vehicle = None
                    felonys = None
                    pass
                return render(request, '1_police_site/run_vin.html', {'role': checkuserrole(request),
                                                                      'search': request.POST['searched'],
                                                                      'vehicle': vehicle,
                                                                      'felonys': felonys,
                                                                      })
            return render(request, '1_police_site/run_vin.html', {'role': checkuserrole(request)})
        else:
            return redirect('home')
    else:
        return redirect('login')


def display_owner(request, owner_id):
    if request.user.is_authenticated:
        if checkuserrole(request) == 'Police' or checkuserrole(request) == 'Admin':
            vehicle = vehicle_license_plate_registration_table.objects.filter(
                registered_owner_id__pk=owner_id)
            indiv = registered_vehicle_owner_table.objects.get(pk=owner_id)
            form = VehicleOwnerForm(request.POST or None, instance=indiv)
            felonys = IncidentVehicular.objects.filter(
                registered_owner_id__pk=owner_id)
            return render(request, '1_police_site/display_owner.html', {'form': form, 'owner_id': owner_id, 'felonys': felonys, 'indiv': indiv, 'vehicle': vehicle, 'role': checkuserrole(request), })
        else:
            return redirect('home')
    else:
        return redirect('login')


def display_vehicle(request, vin):
    if request.user.is_authenticated:
        if checkuserrole(request) == 'Police' or checkuserrole(request) == 'Admin' or checkuserrole(request) == 'Police':
            vehicle = vehicle_license_plate_registration_table.objects.get(
                pk=vin)
            felonys = IncidentVehicular.objects.filter(vin__pk=vin)

            return render(request, '1_police_site/display_vehicle.html', {'vin': vin, 'vehicle': vehicle, 'felonys': felonys, 'role': checkuserrole(request), })
        else:
            return render(request, 'home/home.html', {'role': checkuserrole(request), })
    else:
        return render(request, 'login/login.html', {'role': checkuserrole(request), })


def display_incident(request, incident_id):
    if request.user.is_authenticated:
        if checkuserrole(request) == 'Police' or checkuserrole(request) == 'Admin':
            report = IncidentVehicular.objects.get(pk=incident_id)
            total_ammout = 0
            for felony in report.felony.all():
                total_ammout = total_ammout + int(felony.felony_charge)
            return render(request, '1_police_site/incident.html', {'role': checkuserrole(request),
                                                                   'total_ammount': total_ammout,
                                                                   'report': report})
        else:
            return redirect('home')
    else:
        return redirect('login')


def generate_incident(request, incident_id):
    if request.user.is_authenticated:
        if checkuserrole(request) == 'Police' or checkuserrole(request) == 'Admin':
            # Create Bytestream Buffer
            buffer = io.BytesIO()
            canv = canvas.Canvas(buffer, pagesize=A4, bottomup=0)
            # Create text object
            textobj = canv.beginText()
            textobj.setTextOrigin(inch, inch)
            textobj.setFont('Times-Roman', 14)

            # Get incident report of that incident id
            incident = IncidentVehicular.objects.get(pk=incident_id)
            # Create Empty List of lines
            lines = []
            # Append the data in the list of lines
            lines.append('')
            lines.append(f'Incident Title: {incident.incident_title}')
            lines.append(
                '___________________________________________________________________')
            lines.append(f'Incident ID: {incident.incident_id}')
            lines.append('')
            felFine = 0

            lines.append('Felonies:')
            for felony in incident.felony.all():
                lines.append(f'  {felony}')
                felFine = felFine + int(felony.felony_charge)

            lines.append('')
            lines.append(f'Total Fine: {felFine} Taka')
            lines.append('')
            lines.append(
                f'Registered Vehicle Owner: {incident.registered_owner_id.registered_vehicle_owner}')
            lines.append('')
            lines.append(
                f'Registered Vehicle OwnerID: {incident.registered_owner_id.registered_owner_id}')
            lines.append('')
            lines.append(f'Vehicle Identification Number: {incident.vin}')
            lines.append('')
            lines.append(f'Submission Date: {incident.submition_date}')
            lines.append('')
            lines.append(f'Submitted By: {incident.submitted_by}')
            lines.append(
                '___________________________________________________________________')

            # Putting lines in text object
            for line in lines:
                textobj.textLine(line)
            # Finishing Up file by generating
            canv.drawText(textobj)
            canv.showPage()
            canv.save()
            buffer.seek(0)

            # Return the generated pdf file
            return FileResponse(buffer, as_attachment=True, filename=f'{incident_id}.pdf')
        else:
            return redirect('home')
    else:
        return redirect('login')


def generate_bill(request, incident_id):
    if request.user.is_authenticated:
        if checkuserrole(request) == 'Police' or checkuserrole(request) == 'Admin':
            # Create Bytestream Buffer
            buffer = io.BytesIO()
            canv = canvas.Canvas(buffer, pagesize=A4, bottomup=0)
            # Create text object
            textobj = canv.beginText()
            textobj.setTextOrigin(inch, inch)
            textobj.setFont('Times-Roman', 10)

            # Get Bill of that incident id
            incident = IncidentVehicular.objects.get(pk=incident_id)
            # Create Empty List of lines
            lines = []
            # Append the data in the list of lines
            lines.append(f'Person Copy')
            lines.append('')
            lines.append('')
            lines.append('')
            lines.append('')
            lines.append(f'Transaction ID: {incident.incident_id}')
            lines.append('')
            lines.append(f'Report Date: {incident.submition_date}')
            lines.append('')
            lines.append(f'Incident ID: {incident.incident_id}')
            lines.append('')
            lines.append(f'Vehicle Identification Number: {incident.vin}')
            lines.append('')
            lines.append(
                f'Registered Vehicle Owner ID: {incident.registered_owner_id.registered_owner_id}')
            lines.append('')
            lines.append(
                f'Registered Vehicle Owner: {incident.registered_owner_id.registered_vehicle_owner}')
            lines.append('')
            felFine = 0

            lines.append('Felonies:')
            for felony in incident.felony.all():
                lines.append(f'  {felony}')
                felFine = felFine + int(felony.felony_charge)

            lines.append('')
            lines.append(f'Net Payable Ammount: {felFine} Taka')
            lines.append('')
            lines.append(
                f'Please pay the Net Payable Ammount: {felFine} Taka to any branch of Sonali Bank')
            lines.append(
                '_________________________________________________________________________________________')
            lines.append('')
            lines.append(f'Bank Copy')
            lines.append('')
            lines.append('')
            lines.append('')
            lines.append('')
            lines.append(f'Transaction ID: {incident.incident_id}')
            lines.append('')
            lines.append(f'Report Date: {incident.submition_date}')
            lines.append('')
            lines.append(f'Incident ID: {incident.incident_id}')
            lines.append('')
            lines.append(f'Vehicle Identification Number: {incident.vin}')
            lines.append('')
            lines.append(
                f'Registered Vehicle Owner ID: {incident.registered_owner_id.registered_owner_id}')
            lines.append('')
            lines.append(
                f'Registered Vehicle Owner: {incident.registered_owner_id.registered_vehicle_owner}')
            lines.append('')
            felFine = 0

            lines.append('Felonies:')
            for felony in incident.felony.all():
                lines.append(f'  {felony}')
                felFine = felFine + int(felony.felony_charge)

            lines.append('')
            lines.append(f'Net Payable Ammount: {felFine} Taka')
            lines.append('')
            lines.append(
                f'Please pay the Net Payable Ammount: {felFine} Taka to any branch of Sonali Bank')

            # Putting lines in text object
            for line in lines:
                textobj.textLine(line)
            # Finishing Up file by generating
            canv.drawText(textobj)
            canv.showPage()
            canv.save()
            buffer.seek(0)

            # Return the generated pdf file
            return FileResponse(buffer, as_attachment=True, filename=f'Bill_of_{incident_id}.pdf')
        else:
            return redirect('home')
    else:
        return redirect('login')

# Generate Vehicle Owner Details for Police


def generate_vehicle_owner_details(request, owner_id):
    if request.user.is_authenticated:
        if checkuserrole(request) == 'Police' or checkuserrole(request) == 'Admin':
            # Create Bytestream Buffer
            buffer = io.BytesIO()
            canv = canvas.Canvas(buffer, pagesize=A4, bottomup=0)
            # Create text object
            textobj = canv.beginText()
            textobj.setTextOrigin(inch, inch)
            textobj.setFont('Times-Roman', 10)

            # Get object of that owner id
            owner = registered_vehicle_owner_table.objects.get(pk=owner_id)
            # Create Empty List of lines
            lines = []
            # Append the data in the list of lines
            lines.append(
                f"Detailed Report on {owner.registered_vehicle_owner}")
            lines.append(
                '_________________________________________________________________________________________')
            lines.append("Registered Owner's details")
            lines.append(
                '_________________________________________________________________________________________')
            lines.append(
                f'Registered Vehicle Owner: {owner.registered_vehicle_owner}')
            lines.append(
                f'registered Vehicle Owner ID: {owner.registered_owner_id}')
            lines.append(
                f"Registered Owner's Address: {owner.registered_owner_address}")
            lines.append(
                f"Registered Vehicle Owner's DOB: {owner.registered_owner_dob}")
            lines.append(
                f"Registration Date: {owner.registered_owner_data_create}")
            lines.append('')
            lines.append(
                '_________________________________________________________________________________________')
            lines.append(f"Registered Owned Vehicle(s)")
            lines.append(
                '_________________________________________________________________________________________')

            vehicles = vehicle_license_plate_registration_table.objects.filter(
                registered_owner_id__pk=owner_id)

            if vehicles:
                for vehicle in vehicles:
                    lines.append(f"City Name: {vehicle.city_name}")
                    lines.append(
                        f"Vehicle Classification: {vehicle.vehicle_classification}")
                    lines.append(f"VIN: {vehicle.vin}")
                    lines.append(f"Engine CC: {vehicle.engine_cc}")
                    lines.append(f"Vehicle Brand: {vehicle.vehicle_brand}")
                    lines.append(
                        f"Vehicle Registered To: {vehicle.registered_owner_id.registered_vehicle_owner}")
                    lines.append('')
                lines.append(
                    '_________________________________________________________________________________________')
            lines.append(
                f"Felonies {owner.registered_vehicle_owner} has been committed")

            felonies = IncidentVehicular.objects.filter(
                registered_owner_id__pk=owner_id)
            lines.append(
                '_________________________________________________________________________________________')
            if felonies:
                for felony in felonies:
                    lines.append(f"Report Title: {felony.incident_title}")
                    lines.append(f"Report ID: {felony.incident_id}")
                    lines.append('')
            if felonies == None:
                lines.append(
                    f"{owner.registered_vehicle_owner} has never been committed any felony(ies)")
            lines.append(
                '_________________________________________________________________________________________')
            lines.append(f"Printed by {request.user}")
            # Putting lines in text object
            for line in lines:
                textobj.textLine(line)
            # Finishing Up file by generating
            canv.drawText(textobj)
            canv.showPage()
            canv.save()
            buffer.seek(0)

            # Return the generated pdf file
            return FileResponse(buffer, as_attachment=True, filename=f'{owner_id}.pdf')
        else:
            return redirect('home')
    else:
        return redirect('login')
