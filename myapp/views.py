from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import *
from .models import *
from django.conf import settings

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
import base64

import re
import pytesseract
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


from PIL import Image


import cv2
import os
import tempfile

from ultralytics import YOLO


def get_vin(name):
    # Defining dictionary to translate bangla numbers to english number
    dicB2E = {
        '০': '0',
        '১': '1',
        '২': '2',
        '৩': '3',
        '৪': '4',
        '8': '4',
        '৫': '5',
        '৬': '6',
        '৭': '7',
        '৮': '8',
        '৯': '9'
    }

    filtDict = {
        '5': 'গ',
        '5|': 'গ',
        '5 |': 'গ',
        '9|': 'গ',
        '[': 'ঢ' ,
        '[1': 'ঢা',
        'মেট্রেো': 'মেট্রো',
        'যেড্রেো': 'মেট্রো',
        'সেটে': 'মেট্রো',
        'মেড্রো': 'মেট্রো',
        'মেঢ্রো': 'মেট্রো',
        'মট্টো': 'মেট্রো',
        'মে্রো': 'মেট্রো',
        'মেস্রো': 'মেট্রো',
        'মেট': 'মেট্রো',
        'সেতো': 'মেট্রো',
        'সেট্রো': 'মেট্রো',
        'মেদ্রো': 'মেট্রো',
        '|': '',
        '.': '',
        'ভাকা': 'ঢাকা',
        'ডাকা': 'ঢাকা',
        '(ঢাকা': 'ঢাকা',
        'কা': 'ঢাকা',
        'ঢাক্কা': 'ঢাকা',
        'ঢাক': 'ঢাকা',
    }

    districts_bd = {
        "ঢাকা": "Dhaka",
        "চট্টগ্রাম": "Chittagong",
        "খুলনা": "Khulna",
        "বরিশাল": "Barisal",
        "ময়মনসিংহ": "Mymensingh",
        "রাজশাহী": "Rajshahi",
        "সিলেট": "Sylhet",
        "রংপুর": "Rangpur",
        "গাজীপুর": "Gazipur",
        "নারায়ণগঞ্জ": "Narayanganj",
        "কুমিল্লা": "Comilla",
        "ফেনী": "Feni",
        "পাবনা": "Pabna",
        "বগুড়া": "Bogra",
        "দিনাজপুর": "Dinajpur",
        "কুষ্টিয়া": "Kushtia",
        "ফরিদপুর": "Faridpur",
        "যশোর": "Jessore",
        "টাঙ্গাইল": "Tangail",
        "মুন্সীগঞ্জ": "Munshiganj",
        "শেরপুর": "Sherpur",
        "নওগাঁ": "Naogaon",
        "লক্ষ্মীপুর": "Lakshmipur",
        "রাজবাড়ী": "Rajbari",
        "সাতক্ষীরা": "Satkhira",
        "চুয়াডাঙ্গা": "Chuadanga",
        "জয়পুরহাট": "Joypurhat",
        "হবিগঞ্জ": "Habiganj",
        "পটুয়াখালী": "Patuakhali",
        "সিরাজগঞ্জ": "Sirajganj",
        "ভোলা": "Bhola",
        "মাগুরা": "Magura",
        "ঝিনাইদহ": "Jhenaidah",
        "নরসিংদী": "Narsingdi",
        "গোপালগঞ্জ": "Gopalganj",
        "মাদারীপুর": "Madaripur",
        "জামালপুর": "Jamalpur",
        "নড়াইল": "Narail",
        "বান্দরবান": "Bandarban",
        "ব্রাহ্মণবাড়িয়া": "Brahmanbaria",
        "কক্সবাজার": "Cox's Bazar",
        "খাগড়াছড়ি": "Khagrachhari",
        "মানিকগঞ্জ": "Manikganj",
        "নীলফামারী": "Nilphamari",
        "রাঙ্গামাটি": "Rangamati",
        "ঠাকুরগাঁও": "Thakurgaon"
    }
    
    
    # Load YOLO models
    ultralytics_model = YOLO('yolov8n.pt')
    license_plate_detector = YOLO(str(settings.BASE_DIR)+'\\myapp\\'+'best.pt')

    # Load image frame
    frame = cv2.imread(str(settings.MEDIA_ROOT)+'\\'+name)
    results = license_plate_detector(frame)

    for i in range(0, len(results[0].boxes.xyxy)):
        x1, y1, x2, y2 = map(int, results[0].boxes.xyxy.tolist()[i])
        cropped_plate = frame[y1:y2, x1:x2]

        gray = cv2.cvtColor(cropped_plate, cv2.COLOR_BGR2GRAY)

        # Preprocess the image to highlight the text regions
        gray = cv2.medianBlur(gray, 5)

    
    
    
        # Extracting all the Text From the Image Frame as Bangla and Parse it to the Data Frame/ Dictionary
        data_with_conf = pytesseract.image_to_data(gray, lang='ben', config='--psm 6', output_type=pytesseract.Output.DICT)
        
        # Extracting all the Text From the Image Frame as Bangla and Parse it to the String
        data = pytesseract.image_to_string(gray, lang='ben', config='--psm 6')
        print(data)

        # Iterate through each word in the data
        for i in range(len(data_with_conf['text'])):
            if int(data_with_conf['conf'][i]) > -1:  # Checking if the confidence is valid
                text = data_with_conf['text'][i]
                conf = data_with_conf['conf'][i]
                
                pattern = r'[\u0985-\u09B9\u09BC-\u09C4\u09C7-\u09CE\u09D7\u09DC-\u09E3]+'
                letters = re.findall(pattern, text)
                numbers = re.findall("[০১২৩৪৫৬৭৮৯]*", text)
                try:
                    print('Bangla Letters in Eng:', districts_bd[f'{letters}'])
                except:
                    print('Bangla Letters:', letters)
                print('Bangla Numbers:', numbers)
                print(f"Detected text: {text} - Confidence: {conf}")
        
        # Using RegEX to filter Bangla Integer Number and store in texts as string
        texts = re.findall("[০১২৩৪৫৬৭৮৯]*", data)
        vins = ""
        for text in texts:
            if text is not None:
                vins = vins + text
        del texts
        vin = ""
        for text in vins:
            # Using Dictionary "dicB2E" convert the Bangla Number to English Integer Number
            vin = vin + str(dicB2E[text])
        del vins
        return vin, cropped_plate

# Function of SMTP Mail the notification to the users
def sendmail(request, subject, message, email_receiver):
    if request.user.is_authenticated:
        if request.user.role == 'Police' or request.user.role == 'Admin' or request.user.role == 'BRTA_Staff':
            email_sender = 'licenseplatetrackingsystem@gmail.com'
            email_password = 'ugpyqehmekreaylw'

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
    # Logging Out of the Session
    logout(request)
    return redirect('login')


def display_home_page(request):
    if request.user.is_authenticated:
        # Rendering the Home Page
        return render(request, 'home/home.html', {  'incident': IncidentVehicular.objects.count(),
                                                    'vehicle': RegisteredVehicle.objects.count(),
                                                    'owner': RegisteredVehicleOwner.objects.count()})
    else:
        return redirect('login')


def register_user(request):
    if request.user.is_authenticated:
        # If the logged in user is an admin
        if request.user.role == 'Admin':
            # Storing the Create User Form in to "form"
            form = CreateUserForm()
            if request.method == "POST":
                # Populating the "form" with the Data acquired from Html form from frontend
                form = CreateUserForm(request.POST)
                # Checking if the Form is valid
                if form.is_valid():
                    # Saving the object into the database after verifying the data
                    form.save()
                    # Showing Success popup message in the screen
                    messages.add_message(
                        request, messages.SUCCESS, 'User Registered Successfully')
                    try:
                        # Sending mail to the newly registered user with the login credentials
                        sendmail(request, f"User Profile Creation of {request.POST['username']}", f"""
Dear {request.POST['username']},
Your Account Registered Successfully as {request.POST['role']}
Your Updated Credentials:
USERNAME: {request.POST['username']}
PASSWORD: {request.POST['password2']}

Regards
License Plate Recognition and Tracking System
""", request.POST['email'])
                    except:
                        pass
                # If the form is not valid
                else:
                    # Show Error popup message in the screen
                    messages.add_message(request, messages.INFO, 'Error')

            return render(request, 'register/register.html', {
                'form': form,
            })
        else:
            return redirect('home')

    else:
        return redirect('login')
# Display and Manage all Users Function
def manage_user(request):
    if request.user.is_authenticated:
        if request.user.role == 'Admin':
            # Show all the active Users in the System from the Customized "User" Model Table from the Database
            return render(request, 'manage/manage_user.html', {'users': User.objects.all(), })
        else:
            return redirect('home')
    else:
        return redirect('login')
# Update a Single and Specific user from the database Function
def update_user(request, user_id):
    if request.user.is_authenticated:
        # Check If the Logged in User is an Admin
        if request.user.role == 'Admin':
            # Get that Specific User using the "user_id"
            try:
                USER = User.objects.get(pk=user_id)
            except:
                return redirect('home')
            # Populate the Form with the User instance from the "user_id"
            form = CreateUserForm(request.POST or None, instance=USER)
            # Checking If the form updated is valid
            if form.is_valid():
                # Saving the updated user object into the User Model in the Database
                form.save()
                # Success message in the screen
                messages.add_message(
                    request, messages.SUCCESS, 'User Information Updated in the Database')
                # Sending updated credentials to the User by Email
                try:
                    sendmail(request, f'User Profile Update of {USER.username}', f"""
Dear {request.POST['username']},
Your Updated Credentials as {request.POST['role']}:
USERNAME: {request.POST['username']}
PASSWORD: {request.POST['password2']}

Regards
License Plate Recognition and Tracking System
""", request.POST['email'])
                except:
                    pass
            return render(request, 'manage/update_user.html', {
                'form': form,
                'userid': user_id,
            })
        else:
            return redirect('home')

    else:
        return redirect('login')
# Function of Delete System user from the Database
def delete_user(request, user_id):
    if request.user.is_authenticated:
        if request.user.role == 'Admin':
            # Get the particular user object using the "user_id"
            USER = User.objects.get(pk=user_id)
            if USER:
                # deleting the user object from the User Model in the Database
                USER.delete()
                # Success message
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
# Function of Registering Vehicle Owner into the RegisteredVehicleOwner Model in the Database
def register_owner(request):
    if request.user.is_authenticated:
        # Checking If the logged in user is "BRTA_Staff" or "Admin"
        if request.user.role == 'BRTA_Staff' or request.user.role == 'Admin':
            # Getting the from for the Model
            form = VehicleOwnerForm()
            # If the User submit the form as post method from the HTML
            if request.method == 'POST':
                # Populate the form of the VehicleOwner with the obtained data
                form = VehicleOwnerForm(request.POST)
                # Checking If the form updated is valid
                if form.is_valid():
                    # Saving the Object in the "RegisteredVehicleOwner" Model in the Database
                    form.save()
                    # Success popup message in the screen
                    messages.add_message(
                        request, messages.SUCCESS, 'Owner Registered in the Database')
                    # Sending Email notification of the Successful Registration into the System to the Registered Person
                    try:
                        sendmail(request, f"Vehicle Owner Registration of {request.POST['registered_vehicle_owner']}", f"""
Dear {request.POST['registered_vehicle_owner']},
Your profile has been Successfully registered into the System

Regards,
License Plate Recognition and Tracking System
						""", request.POST['registered_owner_email'])
                    except:
                        pass
                    return redirect('display-database')
                else:
                    messages.add_message(
                        request, messages.INFO, 'Encoutered Error while Registering Owner')
            return render(request, '1_brta_site/register_owner.html', {'form': form, })
        else:
            return redirect('home')
    else:
        return redirect('login')
# Function of Vehicle Registration to a specific person using "owner_id"
def register_vehicle(request, owner_id):
    if request.user.is_authenticated:
        # Checking If the logged in user is "BRTA_Staff" or "Admin"
        if request.user.role == 'BRTA_Staff' or request.user.role == 'Admin':
            # Getting form of RegisteredVehicle Model from the Database
            form = VehicleRegistrationForm()
            # Getting that specific Vehicle Owner object using "owner_id"
            indivs = RegisteredVehicleOwner.objects.get(pk=owner_id)
            # If the user submitted the form using POST method in the Frontend
            if request.method == 'POST':
                form = VehicleRegistrationForm(request.POST)
                # If the populated form of RegisteredVehicle Model is valid
                if form.is_valid():
                    # Save the Object in the RegisteredVehicle Model in the Database
                    form.save()
                    # Success message to the web screen
                    messages.add_message(
                        request, messages.SUCCESS, 'Registered a vehicle on The Following Owner')
                    # Sending Email notification message of the Successful vehicle Registration into the System to the Vehicle owner
                    try:
                        sendmail(request, f"Successfully Registered Vehicle, VIN: {request.POST['vin']} to {indivs.registered_vehicle_owner}", f"""
Congratulations {indivs.registered_vehicle_owner},
The vehicle with following Cedentials and Identifications
City name: {request.POST['city_name']}, Classification: {request.POST['vehicle_classification']}, VIN: {request.POST['vin']}
Model: {request.POST['vehicle_brand']}, Engine CC: {request.POST['engine_cc']}
Has successfully been registered to "{indivs.registered_vehicle_owner}"

Regards,
License Plate Recognition and Tracking System
""", indivs.registered_owner_email)
                    except:
                        pass

                    return redirect('display-database')
            return render(request, '1_brta_site/register_vehicle.html', {'form': form, 'indivs': indivs, })
        else:
            return redirect('home')
    else:
        return redirect('login')
# Function of displaying the all list of RegisteredVehicle and RegisteredVehicleOwner
def display_database(request):
    if request.user.is_authenticated:
        if request.user.role == 'BRTA_Staff' or request.user.role == 'Admin':
            return render(request, '1_brta_site/display_data_base.html', {
                # getting all the Objects into the Frontend
                'indivs': RegisteredVehicleOwner.objects.all(),
                'vins': RegisteredVehicle.objects.all(),
            })
        else:
            return redirect('home')
    else:
        return redirect('login')

# FUNCTION OF UPDATE VEHICLE OWNER
def update_owner(request, owner_id):
    if request.user.is_authenticated:
        if request.user.role == 'BRTA_Staff' or request.user.role == 'Admin':
     
            form = VehicleOwnerForm(request.POST or None, instance=RegisteredVehicleOwner.objects.get(pk=owner_id))
            if form.is_valid():
                # Saving the model into the database
                form.save()
                # Success message to the web screen
                messages.add_message(
                    request, messages.SUCCESS, 'Vehicle Owner Information Updated in the Database')
                # Sending Email notification of Updating the person's credentials Successfully into the System to the Registered Person
                try:
                    sendmail(request, f"Successfully Updated Registered Owner {request.POST['registered_vehicle_owner']}'s Profile", f"""
					Dear {request.POST['registered_vehicle_owner']},
Your Credentials has been updated

Regards,
License Plate Recognition and Tracking System
""", request.POST['registered_owner_email'])
                except:
                    pass
            # Rendering the HTML page with necessary data
            return render(request, '1_brta_site/manage_person.html', {  'form': form, 
                                                                        'owner_id': owner_id, 
                                                                        'indiv': RegisteredVehicleOwner.objects.get(pk=owner_id), 
                                                                        'vehicle': RegisteredVehicle.objects.filter(registered_owner_id__pk=owner_id), 
                                                                        }
            )
        else:
            return redirect('home')
    else:
        return redirect('login')
# Function of Deleting RegisteredVehicleOwner Object by Primary Key from the database
def delete_owner(request, owner_id):
    if request.user.is_authenticated:
        if request.user.role == 'BRTA_Staff' or request.user.role == 'Admin':
            # Getting RegisteredVehicleOwner Object by Primary Key
            indiv = RegisteredVehicleOwner.objects.get(pk=owner_id)
            if indiv:
                # Deleting the RegisteredVehicleOwner Object
                indiv.delete()
                # Rendering the database page
                return redirect('display-database')
            else:
                return redirect('home')
        else:
            return redirect('home')
    else:
        return redirect('login')
# FUNCTION OF UPDATING A SPECIFIC VEHICLE IN THE DATABASE USING PRIMARY KEY "VIN"
def update_vehicle(request, vin):
    if request.user.is_authenticated:
        if request.user.role == 'BRTA_Staff' or request.user.role == 'Admin':
            vehicle = RegisteredVehicle.objects.get(
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
Dear {RegisteredVehicleOwner.objects.get(pk=vehicle.registered_owner_id.registered_owner_id).registered_vehicle_owner},
Your details of the vehicle with following information City name: {request.POST['city_name']}, Classification: {request.POST['vehicle_classification']}, VIN: {request.POST['vin']}
Model: {request.POST['vehicle_brand']}, Engine CC: {request.POST['engine_cc']}
has been updated

Regards,
License Plate Recognition and Tracking System
""", RegisteredVehicleOwner.objects.get(pk=vehicle.registered_owner_id.registered_owner_id).registered_owner_email)
                except:
                    pass
            return render(request, '1_brta_site/manage_vehicle.html', {'form': form, 'vin': vin, 'vehicle': vehicle, })
        else:
            return redirect('home')
    else:
        return redirect('login')

# FUNCTION FOR DELETING VEHICLE FROM THE DATABASE MODEL
def delete_vehicle(request, vin):
    if request.user.is_authenticated:
        if request.user.role == 'BRTA_Staff' or request.user.role == 'Admin':
            vehicle = RegisteredVehicle.objects.get(
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
        if request.user.role == 'BRTA_Staff' or request.user.role == 'Admin':
            # Create Bytestream Buffer
            buffer = io.BytesIO()
            canv = canvas.Canvas(buffer, pagesize=A4, bottomup=0)
            # Create text object
            textobj = canv.beginText()
            textobj.setTextOrigin(inch, inch)
            textobj.setFont('Times-Roman', 10)

            # Get object of that owner id
            owner = RegisteredVehicleOwner.objects.get(pk=owner_id)
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

            vehicles = RegisteredVehicle.objects.filter(
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

# FUNCTION FOR SEARCHING ITEMS FROM THE DATABASE
def search_item(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            searched = request.POST['searched']
            results_vehicle = RegisteredVehicle.objects.filter(
                Q(vin__contains=searched) |
                Q(city_name__contains=searched) |
                Q(vehicle_classification__contains=searched) |
                Q(vehicle_brand__contains=searched)
            )

            results_owner = RegisteredVehicleOwner.objects.filter(
                Q(registered_owner_id__contains=searched) |
                Q(registered_vehicle_owner__contains=searched)
            )

            return render(request, 'searched/searched.html', {'searched': searched, 'results': results_vehicle, 'results_owner': results_owner, })
        else:
            return redirect('home')
    else:
        return redirect('login')


# POLICE


def checkplate_realtime(request):
    if request.user.is_authenticated:
        if request.user.role == 'Police' or request.user.role == 'Admin':
            if request.method == 'POST':
                image = request.POST['frame_data']
                print(type(image))
                if image:

                    # Remove the header from the base64 encoded data
                    base64_data = image.split(",")[1]

                    # Decode the base64 data
                    binary_data = base64.b64decode(base64_data)

                    # Save the image to a file
                    with open(str(settings.MEDIA_ROOT)+'\\captured.jpg', "wb") as f:
                        f.write(binary_data)
                try:
                    vin, cropped_plate = get_vin('captured.jpg')
                    print('\nvin:', vin)
                    print('\ncropped plate:', type(cropped_plate))
                except:
                    vin = None
                    pass

                try:
                    # Converting the numpy array byte image to a byte stream
                    _, buffer = cv2.imencode('.jpg', cropped_plate)
                    
                    # Convert the byte stream to a base64 encoded string
                    base64_image = base64.b64encode(buffer).decode('utf-8')
                except:
                    base64_image = None
                    pass
                try:
                    fs = FileSystemStorage()
                    # Delete the file after processing
                    fs.delete(str(settings.MEDIA_ROOT)+'\\captured.jpg')
                except:
                    pass
                try:
                    vehicle = RegisteredVehicle.objects.get(pk=vin)
                    felonys = IncidentVehicular.objects.filter(vin__pk=vin)
                except:
                    print('\ntouched null part\n')
                    vehicle = None
                    felonys = None
                
                return render(request, '1_police_site/check_realtime.html', {   'vin': vin, 
                                                                                'vehicle': vehicle, 
                                                                                'felonys': felonys, 
                                                                                'cropped_plate': base64_image})
            return render(request, '1_police_site/check_realtime.html', {})
        else:
            return redirect('home')
    else:
        return redirect('login')

def checkplate_picture(request):
    if request.user.is_authenticated:
        if request.user.role == 'Police' or request.user.role == 'Admin':
            if request.method == 'POST':
                try:
                    image = request.FILES.get('image')
                    print(type(image))
                    # Save the original file
                    fs = FileSystemStorage()
                    saved_file = fs.save(image.name, image)

                    # Get the URL of the saved file
                    saved_file_url = fs.url(saved_file)
                   
                    vin, cropped_plate = get_vin(image.name)

                    print('\nvin:', vin)
                    print('\ncropped plate:', type(cropped_plate))
                    
                    # Converting the numpy array byte image to a byte stream
                    _, buffer = cv2.imencode('.jpg', cropped_plate)
                    
                    # Convert the byte stream to a base64 encoded string
                    base64_image = base64.b64encode(buffer).decode('utf-8')

                    # Delete the file after processing
                    fs.delete(saved_file)
                except:
                    vin = None 
                    base64_image = None
                    pass
                try:
                    vehicle = RegisteredVehicle.objects.get(pk=vin)
                    felonys = IncidentVehicular.objects.filter(vin__pk=vin)
                except:
                    vehicle = None
                    felonys = None

                return render(request, '1_police_site/read_picture.html', { 'vin': vin, 
                                                                            'vehicle': vehicle, 
                                                                            'felonys': felonys,
                                                                            'cropped_plate': base64_image })
            return render(request, '1_police_site/read_picture.html', {})
        else:
            return redirect('home')
    else:
        return redirect('login')


def register_incident(request, vin):
    if request.user.is_authenticated:
        if request.user.role == 'Police' or request.user.role == 'Admin':
            form = IncidentForm()
            if request.method == 'POST':
                form = IncidentForm(request.POST)
                if form.is_valid():
                    instance = form.save()
                    messages.add_message(
                        request, messages.SUCCESS, 'Incident Registered Successfully')
                    vehicle = RegisteredVehicle.objects.get(
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
License Plate Recognition and Tracking System
""", instance.registered_owner_id.registered_owner_email)
                    except:
                        pass
                    return render(request, '1_police_site/display_vehicle.html', {'vin': vin, 'vehicle': vehicle, 'felonys': felonys, })
            vehicle = RegisteredVehicle.objects.get(
                pk=vin)
            return render(request, '1_police_site/register_incident.html', {'form': form,
                                                                            'vehicle': vehicle,
                                                                            })
        else:
            return redirect('home')
    else:
        return redirect('login')


def run_vin(request):
    if request.user.is_authenticated:
        if request.user.role == 'Police' or request.user.role == 'Admin':
            if request.method == 'POST':
                try:
                    vehicle = RegisteredVehicle.objects.get(
                        pk=request.POST['searched'])
                    felonys = IncidentVehicular.objects.filter(
                        vin__pk=request.POST['searched'])
                except:
                    vehicle = None
                    felonys = None
                    pass
                return render(request, '1_police_site/run_vin.html', {'search': request.POST['searched'],
                                                                      'vehicle': vehicle,
                                                                      'felonys': felonys,
                                                                      })
            return render(request, '1_police_site/run_vin.html', {})
        else:
            return redirect('home')
    else:
        return redirect('login')


def display_owner(request, owner_id):
    if request.user.is_authenticated:
        if request.user.role == 'Police' or request.user.role == 'Admin':
            vehicle = RegisteredVehicle.objects.filter(
                registered_owner_id__pk=owner_id)
            indiv = RegisteredVehicleOwner.objects.get(pk=owner_id)
            form = VehicleOwnerForm(request.POST or None, instance=indiv)
            felonys = IncidentVehicular.objects.filter(
                registered_owner_id__pk=owner_id)
            return render(request, '1_police_site/display_owner.html', {'form': form, 'owner_id': owner_id, 'felonys': felonys, 'indiv': indiv, 'vehicle': vehicle, })
        else:
            return redirect('home')
    else:
        return redirect('login')


def display_vehicle(request, vin):
    if request.user.is_authenticated:
        if request.user.role == 'Police' or request.user.role == 'Admin' or request.user.role == 'Police':
            vehicle = RegisteredVehicle.objects.get(
                pk=vin)
            felonys = IncidentVehicular.objects.filter(vin__pk=vin)

            return render(request, '1_police_site/display_vehicle.html', {'vin': vin, 'vehicle': vehicle, 'felonys': felonys,})
        else:
            return render(request, 'home/home.html', {})
    else:
        return render(request, 'login/login.html', {})


def display_incident(request, incident_id):
    if request.user.is_authenticated:
        if request.user.role == 'Police' or request.user.role == 'Admin':
            report = IncidentVehicular.objects.get(pk=incident_id)
            total_amount = 0
            for felony in report.felony.all():
                total_amount = total_amount + int(felony.felony_charge)
            return render(request, '1_police_site/incident.html', {'total_amount': total_amount,
                                                                   'report': report})
        else:
            return redirect('home')
    else:
        return redirect('login')


def generate_incident(request, incident_id):
    if request.user.is_authenticated:
        if request.user.role == 'Police' or request.user.role == 'Admin':
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
        if request.user.role == 'Police' or request.user.role == 'Admin':
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
            lines.append(f'Net Payable Amount: {felFine} Taka')
            lines.append('')
            lines.append(
                f'Please pay the Net Payable Amount: {felFine} Taka to any branch of Sonali Bank')
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
            lines.append(f'Net Payable Amount: {felFine} Taka')
            lines.append('')
            lines.append(
                f'Please pay the Net Payable Amount: {felFine} Taka to any branch of Sonali Bank')

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
        if request.user.role == 'Police' or request.user.role == 'Admin':
            # Create Bytestream Buffer
            buffer = io.BytesIO()
            canv = canvas.Canvas(buffer, pagesize=A4, bottomup=0)
            # Create text object
            textobj = canv.beginText()
            textobj.setTextOrigin(inch, inch)
            textobj.setFont('Times-Roman', 10)

            # Get object of that owner id
            owner = RegisteredVehicleOwner.objects.get(pk=owner_id)
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

            vehicles = RegisteredVehicle.objects.filter(
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
