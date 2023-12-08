from django.shortcuts import render,redirect,reverse
from django.views.generic import TemplateView
from .models import User, Organization, Volunteer, Pets, Appointment, Highlights, Veterinarian, Services, VolunteerRecord, BusinessHours, AppointmentTime, PetMedicalRecord, PetBreed
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout,authenticate,login
from django.utils import timezone
from datetime import datetime, timedelta, time, date
from django.core import serializers
current_date = timezone.now().date()
from asgiref.sync import async_to_sync
from django.db.models import Sum, Min
from django.db import transaction
from django.db.models import Q
orgID = ""
@login_required
def protected_view(request):
    # Your protected view logic here
    return render(request,'LoginPage.html')

def logout_view(request):
    request.session.flush()
    logout(request)
    return redirect('/main')

def get_volunteer_count(request):
    user = User.objects.get(email=request.session['username'])
    organization = Organization.objects.get(user_id=user.id)
    records = VolunteerRecord.objects.filter(org_id=organization.id, volunteerstatus=1)
    volunteer_ids = records.values_list('volunteer_id', flat=True)
    volunteers = Volunteer.objects.filter(id__in=volunteer_ids)

    return volunteers.count()


# Create your views here.
class MainPage(TemplateView):
    template_name = 'MainPage.html'
    def get(self,request):
        try:
            users = User.objects.get(email = request.session['username'])
            if users.usertype == 3:
                return redirect('/orghome')
            elif users.usertype == 7:
                request.session.flush()
                return render(request,'MainPage.html')
            elif users.usertype != 3 and users.usertype != 7:
                return redirect('/userhome')
        except Exception as e:
            return render(request,'MainPage.html')

class DonatePage (TemplateView):
    template_name = 'DonatePage.html'
    def get(self,request):
        organizations = Organization.objects.filter(organizationstatus=2)

        return render(request, 'DonatePage.html', {"organizations": organizations})

class VolunteerOrgPage(TemplateView):
    template_name = 'VolunteerOrgPage.html'

    def get(self,request):
        organizations = Organization.objects.filter(organizationstatus=2)

        return render(request, 'VolunteerOrgPage.html', {"organizations": organizations})

class VolunteerPage (TemplateView):
    template_name = 'VolunteerPage.html'
    def post(self,request):
        current_datetime = timezone.now()
        org_cookie_value = request.COOKIES.get('orgIdVolunteer', '')
        user_id = ""
        password1 = request.POST.get('password')
        password2 = request.POST.get('confirmPassword')

        if password1 != password2:
            return JsonResponse({'noData' : False, 'error' : 'Password do not match!'})
        try:
            try:
                existing_user = User.objects.get(Q(email=request.POST['email']))
            except:
                existing_user = ""

            try:
                existing_user1 = User.objects.get(Q(contactnumber=request.POST['number']))
            except:
                existing_user1 = ""
            if existing_user and existing_user1:
                error = "Email and Contact Number Already Used"
            elif existing_user:
                error = "Email Already Used"
            elif existing_user1:
                error = "Contact Number Already Used"
            return JsonResponse({'noData': False, 'error':error})
        except:

            org = Organization.objects.get(id = org_cookie_value)
            user = User.objects.create_superuser(firstname = request.POST['firstname'], lastname = request.POST['lastname'],
                                        contactnumber = request.POST['contactnumber'], address = request.POST['address'],
                                        email = request.POST['email'], usertype = 2, password = request.POST['password'] )
            user.save()
            volunteer = Volunteer.objects.create(user = user, idpicture = request.FILES['validID'], idpictureback=request.FILES['validID1'])
            volunteer.save()

            try:
                volunteerRecords = VolunteerRecord.objects.create(dateapproved = current_datetime, org_id = org.id, volunteer_id = volunteer.id)
            except:
                volunteerRecords = VolunteerRecord.objects.create(dateapproved = current_datetime, org_id = org, volunteer_id = volunteer)

            volunteerRecords.save()
            return JsonResponse({'noData': True})

class RegisterPage(TemplateView):
    template_name = 'RegisterPage.html'
    def get(self,request):
        try:
            users = User.objects.get(email = request.session['username'])
            if users.usertype == 3:
                return redirect('/orghome')
            elif users.usertype == 7:
                request.session.flush()
                return render(request, 'RegisterPage.html')
            elif users.usertype != 3 and users.usertype != 7:
                return redirect('/userhome')
        except Exception as e:
            return render(request, 'RegisterPage.html')

    def post(self,request):
        usertype = request.POST.get('usertype')
        password1 = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password1 != password2:
            return JsonResponse({'noData' : False, 'error' : 'Password do not match!'})

        if request.POST['usertype'] == "client":
            try:
                user = User.objects.create_superuser(firstname = request.POST['firstname'], lastname = request.POST['lastname'],
                                                    contactnumber = request.POST['contactnumber'], address = request.POST['address'],
                                                    email = request.POST['email'], usertype = 1, password = request.POST['password'] )
                user.save()
                return JsonResponse({'noData': True})
            except Exception as e:
                print(f"An error occurred: {e}")
                return JsonResponse({'noData': False, 'error': str(e)})
        else:

            if request.POST['clinic_password'] != request.POST['clinic_password2']:
                return JsonResponse({'noData' : False, 'error' : 'Password do not match!'})
            try:
                try:
                    existing_user = User.objects.get(Q(email=request.POST['clinic_email']))
                except:
                    existing_user = ""

                try:
                    existing_user1 = User.objects.get(Q(contactnumber=request.POST['contact_number']))
                except:
                    existing_user1 = ""
                if existing_user and existing_user1:
                    error = "Email and Contact Number Already Used"
                elif existing_user:
                    error = "Email Already Used"
                elif existing_user1:
                    error = "Contact Number Already Used"
                return JsonResponse({'noData': False, 'error':error})
            except:
                user = User.objects.create_superuser(firstname = "org", lastname = "org",
                                                    contactnumber = request.POST['contact_number'], address = request.POST['clinic_location'],
                                                    email = request.POST['clinic_email'], usertype = 3, password = request.POST['clinic_password'] )
                user.save()
                organization = Organization.objects.create(organization_name = request.POST['organization_name'], user = user,
                                                        cliniclogo = request.FILES['cliniclogo'],
                                                        qrcodebuymeacoffee = request.FILES['qrcodebuymeacoffee'], qrcodegcash = request.FILES['qrcodegcash'],
                                                        qrcodepaypal = request.FILES['qrcodepaypal'], certificate_of_accreditation = request.FILES['certificate_of_accreditation'])
                organization.save()
                checked_values = request.POST.getlist('days[]')
                lunch_start = datetime.strptime('12:00', '%H:%M').time()
                lunch_end = datetime.strptime('13:00', '%H:%M').time()

                for day in checked_values:
                    time_in = request.POST.get(f"time_in_{day}")
                    time_out = request.POST.get(f"time_out_{day}")

                    if time_in and time_out:
                        time_in = datetime.strptime(time_in, '%H:%M')
                        time_out = datetime.strptime(time_out, '%H:%M')

                        business = BusinessHours.objects.create(
                            day=day,
                            open_time=time_in.time(),
                            close_time=time_out.time(),
                            organization_id=organization.id
                        )
                        business.save()

                        current_time = time_in
                        while current_time < time_out:
                            if current_time.time() < lunch_start or current_time.time() >= lunch_end:
                                AppointmentTime.objects.create(appointment_time=current_time.time().strftime('%H:%M'), businesshours=business)

                            current_time += timedelta(minutes=60)
                services = Services.objects.filter(organization_id=organization.id).exists()

                if not services:
                    Services.objects.create(service_offered="Spay/Neuter Surgery", organization_id=organization.id, duration=30)
                    Services.objects.create(service_offered="Vaccination", organization_id=organization.id, duration=10)
                    Services.objects.create(service_offered="Deworming", organization_id=organization.id, duration=10)
                    Services.objects.create(service_offered="Checkup", organization_id=organization.id, duration=15)

                return JsonResponse({'noData': True, 'org': request.POST['organization_name']})


class LoginPage (TemplateView):
    template_name = 'LoginPage.html'

    def get(self,request):
        try:
            users = User.objects.get(email = request.session['username'])
            if users.usertype == 7:
                request.session.flush()
                return render(request,'LoginPage.html')
            else:
                return redirect('/main')

        except Exception as e:
            return render(request,'LoginPage.html')
    def post(self,request):
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request,email=email,password=password)
        if user is not None:
            login(request,user)
            request.session['username'] = email
            request.session.save()
            user = User.objects.get(email = request.session['username'])
            return JsonResponse({'noData': False, 'usertype': user.usertype})
        else:

            return JsonResponse({'noData': True, 'error': "Invalid Email or Password!"})


class UserDashboard( LoginRequiredMixin, TemplateView):
    template_name = 'UserDashboard.html'
    def get(self,request):
        users = User.objects.get(email = request.session['username'])
        return render(request, 'UserDashboard.html', {"users" : users})

class UserProfilePage(LoginRequiredMixin, TemplateView):
    template_name = 'UserProfilePage.html'

    def get(self,request):
        try:
            users = User.objects.get(email = request.session['username'])
            if users.usertype == 3:
                 return render(request, 'UserHomePage.html', {"error": "You don't have permission to access this web page!"})
            return render(request, 'UserProfilePage.html', {"users" : users})
        except Exception as e:
            print(e)
            return redirect('/main')


    def post(self,request):
        user = User.objects.get(id= request.POST['userid'])
        user.userphoto = request.FILES['profile'] if 'profile' in request.FILES else user.userphoto
        user.firstname = request.POST['firstname']
        user.lastname = request.POST['lastname']
        user.contactnumber = request.POST['contactnumber']
        user.email = request.POST['email1']

        user.save()
        return JsonResponse({'accepted': True})


class UserHomePage(LoginRequiredMixin, TemplateView):
    template_name = 'UserHomePage.html'


    def get(self,request):
        users = User.objects.get(email = request.session['username'])
        if users.usertype == 3:
            return render(request, 'UserHomePage.html', {"error": "You don't have permission to access this web page!"})
        try:
            pets = PetBreed.objects.exists()
            if not pets:
                PetBreed.objects.create(pet_breed='Aspin', pet_type="dog")
                PetBreed.objects.create(pet_breed='Shih Tzu', pet_type="dog")
                PetBreed.objects.create(pet_breed='Chow Chow', pet_type="dog")
                PetBreed.objects.create(pet_breed='Poodle', pet_type="dog")
                PetBreed.objects.create(pet_breed='Golden Retriever', pet_type="dog")
                PetBreed.objects.create(pet_breed='Siberian Husky', pet_type="dog")
                PetBreed.objects.create(pet_breed='Pug', pet_type="dog")
                PetBreed.objects.create(pet_breed='Pomeranian', pet_type="dog")
                PetBreed.objects.create(pet_breed='German Shepherd', pet_type="dog")
                PetBreed.objects.create(pet_breed='Beagle', pet_type="dog")
                PetBreed.objects.create(pet_breed='Puspin', pet_type="cat")
                PetBreed.objects.create(pet_breed='Siamese', pet_type="cat")
                PetBreed.objects.create(pet_breed='Himalayan', pet_type="cat")
                PetBreed.objects.create(pet_breed='Persian', pet_type="cat")
                PetBreed.objects.create(pet_breed='Russian Blue', pet_type="cat")
                PetBreed.objects.create(pet_breed='Chinchilla', pet_type="cat")
                PetBreed.objects.create(pet_breed='Tonkinese', pet_type="cat")
                PetBreed.objects.create(pet_breed='Birman', pet_type="cat")
                PetBreed.objects.create(pet_breed='Korat', pet_type="cat")
                PetBreed.objects.create(pet_breed='Tiffanie', pet_type="cat")
            organizations = Organization.objects.filter(organizationstatus=2)
            veterinarians = Veterinarian.objects.all()
            highlights = Highlights.objects.all()
            pets = Pets.objects.filter(user_id = users.id)
            volunteerRecords = VolunteerRecord.objects.all()
            volunteers = Volunteer.objects.all()
            data = []
            for organization in organizations:
                try:
                    volunteer = Volunteer.objects.get(user_id = users.id)
                    organization_exists_in_records = volunteerRecords.get(org_id=organization.id, volunteer_id=volunteer.id)
                except:
                    organization_exists_in_records = False

                if organization_exists_in_records:
                    organization_exists_in_records = True
                    volunteer = Volunteer.objects.get(user_id = users.id)
                    try:
                        volunteer_get_status = VolunteerRecord.objects.get(org_id = organization.id, volunteer_id = volunteer.id)
                        volunteer_status = volunteer_get_status.volunteerstatus
                    except:
                        volunteer_status = None
                else:
                    volunteer_status = None
                data.append({
                    'id': organization.id,
                    'cliniclogo': organization.cliniclogo,
                    'organization_name': organization.organization_name,
                    'address': organization.user.address,
                    'contactnumber': organization.user.contactnumber,
                    'organization_exists_in_records': organization_exists_in_records,
                    'volunteer_status': volunteer_status
                })
            return render(request, 'UserHomePage.html', {"veterinarians" : veterinarians ,"organizations": data, "pets": pets,
            "highlights": highlights, 'volunteerRecords': volunteerRecords, "users": users})
        except Exception as e:
             return render(request, 'UserHomePage.html', {"error": "You don't have permission to access this web page!"})

    def post(self,request):
        org_cookie_value = request.COOKIES.get('orgstr', '')
        vet_cookie_value = request.COOKIES.get('getVetstr', '')
        user = User.objects.get(email = request.session['username'])

        if request.POST.get('orgHiddenId'):
            client_volunteer = Volunteer.objects.create(user_id = user.id, idpicture = request.FILES['validID'], idpictureback=request.FILES['validID1'])

            client_volunteer.save()
            user.usertype = 5
            user.save()
            volunteer = Volunteer.objects.get(user_id = user.id)
            current_datetime = timezone.now()
            record = VolunteerRecord.objects.create(volunteer_id = volunteer.id, org_id = request.POST['orgHiddenId'], dateapproved = current_datetime)
            record.save()

            return redirect('/userhome')
        elif request.POST.get('servicesID'):  # Use .get() to avoid KeyError if 'vetID' is not in POST data
            vetID = request.POST['servicesID']
            businesshours = BusinessHours.objects.filter(organization_id=vetID)
            services = Services.objects.filter(organization_id=vetID, is_active=True)
            data = {
                'services': list(services.values()),
                'businesshours': list(businesshours.values('day'))
            }
            return JsonResponse(data)

        elif request.POST.get('vetID'):  # Use .get() to avoid KeyError if 'vetID' is not in POST data
            vetID = request.POST['vetID']
            veterinarians = Veterinarian.objects.filter(organization_id=vetID)
            data = {'veterinarians': list(veterinarians.values())}
            return JsonResponse(data)

        elif request.POST.get('orgIdHidden'):
            volunteer = Volunteer.objects.get(user_id = user.id)
            volunteer.idpicture = request.FILES['validID2']
            volunteer.idpictureback = request.FILES['validID3']
            current_datetime = timezone.now()
            record = VolunteerRecord.objects.create(volunteer_id = volunteer.id, org_id = request.POST['orgIdHidden'], dateapproved = current_datetime)
            volunteer.save()
            record.save()
            return redirect('/userhome')

        elif request.POST.get('isBusinessHours'):
            appointment_date_str = request.POST['appointmentdate']
            appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d')
            day_name = appointment_date.strftime('%A')
            businessHours = BusinessHours.objects.get(organization_id=org_cookie_value, day=appointment_date.strftime('%A')[:3].lower())
            appointments_time = AppointmentTime.objects.filter(businesshours_id=businessHours.id)
            data = {'appointments_time': list(appointments_time.values())}
            return JsonResponse(data)
        elif request.POST.get('isBusinessHoursDate'):
            appointments = Appointment.objects.filter(appointmentdate=request.POST['date_appointed'], appointmenttime=request.POST['time_appointed'], appointed_to=org_cookie_value)
            total_duration = 0
            service = Services.objects.get(organization_id=org_cookie_value, service_offered=request.POST['servicesType'])
            for appointment in appointments:
                services = Services.objects.filter(organization_id=org_cookie_value, service_offered=appointment.servicetype)
                total_duration += services.aggregate(total_duration=Sum('duration'))['total_duration']
            try:
                min_duration = services.aggregate(min_duration=Min('duration'))['min_duration']
            except:
                min_duration = 0
            data = {'appointments': appointments.count(),  'total_duration': total_duration, 'min_duration': min_duration, 'choosen_service_duration' : service.duration}
            return JsonResponse(data)

        else:
            user = User.objects.get(email = request.session['username'])
            appointment_date_str = request.POST['appointmentdate']
            appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d')
            day_name = appointment_date.strftime('%A')
            businessHours = BusinessHours.objects.get(organization_id=org_cookie_value, day=appointment_date.strftime('%A')[:3].lower())
            appointments_time = AppointmentTime.objects.get(businesshours_id=businessHours.id, appointment_time = request.POST['appointmenttime'])
            appointments_time.save()
            selected_pets = request.POST.getlist('pettobring')
            for pet_id in selected_pets:
                appointments = Appointment.objects.create(appointmentdate = request.POST['appointmentdate'], appointmenttime = request.POST['appointmenttime'],
                                                        servicetype = request.POST['servicetype'], appointed_to_id = org_cookie_value , appointed_by_id = user.id, pettobring_id = pet_id, petmedicalrecord_id="")

                appointments.save()

            return redirect('/userappointments')



class UserAppointmentsPage( LoginRequiredMixin, TemplateView):
    template_name = 'UserAppointmentsPage.html'
    def get(self,request):
        try:
            users = User.objects.get(email = request.session['username'])
            pets = Pets.objects.filter(user_id = users.id)
            pet_ids = [pet.id for pet in pets]

            # Get current date and time
            current_datetime = timezone.now()

            # Fetch future appointments (appointments with a start date/time greater than the current date/time)
            future_appointments = Appointment.objects.filter(
                pettobring_id__in=pet_ids,
                appointmentdate__gte=current_datetime
            )

            # Fetch past appointments (appointments with a start date/time less than or equal to the current date/time)
            past_appointments = Appointment.objects.filter(
                pettobring_id__in=pet_ids,
                appointmentdate__lt=current_datetime
            )

            return render(request, 'UserAppointmentsPage.html', {
                "appointments": future_appointments,
                "past_appointments": past_appointments,
                'users': users
            })
        except Exception as e:
            return render(request, 'UserHomePage.html', {"error": "You don't have permission to access this web page!"})

class UserPetsPage( LoginRequiredMixin, TemplateView):
    template_name = 'UserPetsPage.html'

    def get(self,request):


        def calculate_age(birthdate):
            # Assuming birthdate is a string in the format 'YYYY-MM-DD'

            birthdate_obj = birthdate
            date_today = datetime.now()

            age_years = date_today.year - birthdate_obj.year
            month_gap = date_today.month - birthdate_obj.month

            if month_gap < 0 or (month_gap == 0 and date_today.day < birthdate_obj.day):
                age_years -= 1

            age_months = date_today.month - birthdate_obj.month

            if date_today.day < birthdate_obj.day:
                age_months -= 1
                age_months = (age_months + 12) % 12

            age_string = ''
            if age_years > 0:
                age_string += f'{age_years} {"year" if age_years == 1 else "years"}'
            if age_months > 0:
                if age_string:
                    age_string += ' and '
                age_string += f'{age_months} {"month" if age_months == 1 else "months"}'
            if age_string == '':
                age_string = "Less than 1 month"
            return age_string
        try:
            users = User.objects.get(email = request.session['username'])

            pets = Pets.objects.filter(user_id = users.id)
            for pet in pets:
                age = calculate_age(pet.pet_birthdate)
                pet.pet_age = age
                pet.save()

            return render(request, 'UserPetsPage.html', {"pets": pets,  "users" : users})
        except Exception as e:
            return render(request, 'UserHomePage.html', {"error": "You don't have permission to access this web page!"})
    def post(self,request):
        if request.POST.get('pet_type_breeds'):
            pet_breeds = PetBreed.objects.filter(pet_type=request.POST['pet_type_breeds'])

            pet_breeds_list = [
                {
                    'breed': breed.pet_breed
                }
                for breed in pet_breeds
            ]
            return JsonResponse({'breeds': pet_breeds_list})
        else:
            user = User.objects.get(email = request.session['username'])
            pets = Pets.objects.create(user_id = user.id, pet_picture = request.FILES['pet_picture'], pet_name = request.POST['pet_name'], pet_type = request.POST['pet_type'],
                                    pet_breed = request.POST['pet_breed'], pet_birthdate = request.POST['pet_birthdate'],
                                    pet_age = request.POST['pet_age'], pet_gender = request.POST['pet_gender'] )

            pets.save()
            return redirect('/userpets')


class UserHighlightsPage( LoginRequiredMixin, TemplateView):
    template_name = 'UserHighlightsPage.html'

    def get(self,request):
        try:
            users = User.objects.get(email = request.session['username'])
            volunteer = Volunteer.objects.get(user_id = users.id)
            highlights = Highlights.objects.filter(volunteer_id = volunteer.id)

            return render(request, 'UserHighlightsPage.html', {"highlights" : highlights, 'users':users})
        except Exception as e:
            return render(request, 'UserHomePage.html', {"error": "You don't have permission to access this web page!"})

    def post(self,request):
        user = User.objects.get(email = request.session['username'])
        volunteer = Volunteer.objects.get(user_id = user.id)
        highlights = Highlights.objects.create(highlightstitle = request.POST['highlightstitle'], highlightsphoto = request.FILES['volunteerphoto'], highlightsdescription = request.POST['volunteerdescription'], volunteer_id = volunteer.id)

        highlights.save()

        return redirect('/userhighlights')


class OrgDashboard(TemplateView):
    template_name = 'OrgDashboard.html'

    def get(self, request):

        volunteer_count = get_volunteer_count(request)

        return render(request, 'OrgDashboard.html', {"volunteers": volunteers, "volunteer_count": volunteer_count})


class OrgHomePage( LoginRequiredMixin, TemplateView):
    template_name = 'OrgHomePage.html'
    def get(self,request):
        try:
            users = User.objects.get(email = request.session['username'])
            unique_dates = set()
            organization = Organization.objects.get(user_id = users.id)
            veterinarians = Veterinarian.objects.filter(organization_id = organization.id)
            services = Services.objects.filter(organization_id = organization.id)
            appointments = Appointment.objects.filter(appointed_to_id = organization.id)


            volunteer_count = get_volunteer_count(request)
            unique_dates_list = []
            for appointment in appointments:
                date_str = appointment.appointmentdate.strftime('%Y-%m-%d')
                # Check if the date is not already in the set
                if date_str not in unique_dates:
                    unique_dates.add(date_str)
                    unique_dates_list.append({'date': date_str})
            appointments_list = [

                {
                    'id': appointment.id,
                    'name': appointment.appointed_by.firstname + " " + appointment.appointed_by.lastname,
                    'date': appointment.appointmentdate.strftime('%Y-%m-%d'),
                    'time': appointment.appointmenttime.strftime('%H:%M:%S'),
                    'status': appointment.appointmentstatus,
                    'pet': appointment.pettobring.pet_name,
                    'service': appointment.servicetype,
                    # Add more fields as needed
                }
                for appointment in appointments
            ]
            return render(request, 'OrgHomePage.html', {"org": organization, "user": users, "veterinarians" : veterinarians, "services" : services, "appointments": appointments_list, 'appointment_dates': unique_dates_list, "volunteer_count": volunteer_count })
        except:
            return render(request, 'OrgHomePage.html', {"error": "You don't have permission to access this web page!"})
    def post(self,request):
        user = User.objects.get(email = request.session['username'])
        organization = Organization.objects.get(user_id = user.id)

        if request.POST.get('vetname'):
            veterinarians = Veterinarian.objects.create(organization_id = organization.id, profilepicture = request.FILES['profilepicture'], vetname = request.POST['vetname'], vetdescription = request.POST['vetdescription'])

            veterinarians.save()

            return redirect('/orghome')

        elif request.POST.get('isButtonClicked'):
            day_name = date(int(request.POST["year"]), int(request.POST["month"]), int(request.POST["day"])).strftime('%A')[:3].lower()
            businesshours = BusinessHours.objects.get(organization_id = organization.id, day=day_name)

            appointments_time = AppointmentTime.objects.filter(businesshours_id = businesshours.id)
            appointments_list = [
                {'appointment_time': appointment.appointment_time.strftime('%H:%M')}
                for appointment in appointments_time
            ]

            return JsonResponse({'appointments_time': appointments_list})

        elif request.POST.get('service_offered'):
            services = Services.objects.create(organization_id = organization.id, service_offered = request.POST['service_offered'], duration=request.POST['service_duration'])

            services.save()

            return redirect('/orghome')

        elif request.POST.get('service_id'):
            services = Services.objects.get(id = request.POST["service_id"])
            services.delete()

            return self.get(request)

        elif request.POST.get('service_id_duration'):
            services = Services.objects.get(id = request.POST["service_id_duration"])
            services.duration = request.POST["duration"]
            services.save()
            return self.get(request)
        elif request.POST.get('service_id_switch'):
            services = Services.objects.get(id = request.POST["service_id_switch"])
            services.is_active = not services.is_active
            services.save()
            return redirect('/orghome')

        elif request.POST.get('button'):

            if request.POST.get('button') == 'check':
                appointment = Appointment.objects.get(id=request.POST['appointmentId'])
                email = appointment.appointed_by.email
                org = appointment.appointed_to.organization_name
                appointment_date = appointment.appointmentdate

                day_name = appointment_date.strftime('%A')[:3].lower()
                user = User.objects.get(email=request.session['username'])
                organization = Organization.objects.get(user_id=user.id)
                businessHours = BusinessHours.objects.get(organization_id=organization.id, day=day_name)
                date_string = appointment_date.strftime("%Y-%m-%d")
                # Use 'appointment.appointmenttime' directly (assuming it's already a datetime.time object)
                appointment_time = appointment.appointmenttime

                appointment.appointmentstatus = 'accepted'
                appointment.save()
                return JsonResponse({'accepted': True, 'email' : email, 'org' : org, 'date' : date_string, 'time': appointment.appointmenttime.strftime('%H:%M:%S')})



            else:
                appointment_id = request.POST['appointmentId']
                id_appointment = int(appointment_id[1:])
                appointment = Appointment.objects.get(id = id_appointment)
                email = appointment.appointed_by.email
                org = appointment.appointed_to.organization_name
                appointment_date = appointment.appointmentdate
                date_string = appointment_date.strftime("%Y-%m-%d")
                appointment.delete()
                return JsonResponse({'accepted': False, 'email' : email, 'org' : org, 'date' : date_string, 'time': appointment.appointmenttime.strftime('%H:%M:%S')})

        return redirect('/orghome')


class OrgProfilePage( LoginRequiredMixin, TemplateView):
    template_name = 'OrgProfilePage.html'

    def get(self, request):
        try:
            users = User.objects.get(email = request.session['username'])
            organization = Organization.objects.get(user=users)
            businesshours = BusinessHours.objects.filter(organization_id=organization.id)
            volunteer_count = get_volunteer_count(request)
            return render(request, 'OrgProfilePage.html', {"organization": organization, "user": users, "businesshours": businesshours, 'volunteer_count':volunteer_count})
        except:
            return render(request, 'OrgHomePage.html', {"error": "You don't have permission to access this web page!"})

    def post(self,request):
        if request.POST.get('isChecked'):
            lunch_start = datetime.strptime('12:00', '%H:%M').time()
            lunch_end = datetime.strptime('13:00', '%H:%M').time()
            users = User.objects.get(email = request.session['username'])
            organization = Organization.objects.get(user=users)
            if request.POST['isChecked'] == "false":
                businesshours = BusinessHours.objects.filter(organization_id=organization.id, day=request.POST['day'])
                businesshours.delete()
            else:
                try:
                    business_hours_exist = BusinessHours.objects.get(organization_id=organization.id, day=request.POST['day'])
                    appointment = AppointmentTime.objects.filter(businesshours_id = business_hours_exist.id)
                    appointment.delete()
                    business_hours_exist.open_time = request.POST['time_in']
                    business_hours_exist.close_time = request.POST['time_out']
                    business_hours_exist.save()
                    current_time = datetime.strptime(request.POST['time_in'], '%H:%M')
                    while current_time < datetime.strptime(request.POST['time_out'],'%H:%M'):
                        if current_time.time() < lunch_start or current_time.time() >= lunch_end:
                            AppointmentTime.objects.create(appointment_time=current_time.time().strftime('%H:%M'), businesshours=business_hours_exist)
                        current_time += timedelta(minutes=60)
                except:
                    businesshours = BusinessHours.objects.create(organization_id=organization.id, open_time=request.POST['time_in'], close_time=request.POST['time_out'], day=request.POST['day'])
                    businesshours.save()
                    current_time = datetime.strptime(request.POST['time_in'], '%H:%M')
                    while current_time < datetime.strptime(request.POST['time_out'],'%H:%M'):
                        if current_time.time() < lunch_start or current_time.time() >= lunch_end:
                            AppointmentTime.objects.create(appointment_time=current_time.time().strftime('%H:%M'), businesshours=businesshours)
                        current_time += timedelta(minutes=60)
            return JsonResponse({'switched': True})

        else:
            organization = Organization.objects.get(id= request.POST['organization_id'])
            organization.cliniclogo = request.FILES['profileorg'] if 'profileorg' in request.FILES else organization.cliniclogo
            organization.organization_name = request.POST['nameoforg']
            organization.user.contactnumber = request.POST['contactnumber']
            organization.user.address = request.POST['address']
            organization.user.email = request.POST['email1']

            # Check and update certificate_of_accreditation field
            if 'accreditationcertificate' in request.FILES:
                organization.certificate_of_accreditation = request.FILES['accreditationcertificate']

            # Check and update qrcodebuymeacoffee field
            if 'buymeacoffee' in request.FILES:
                organization.qrcodebuymeacoffee = request.FILES['buymeacoffee']

            # Check and update qrcodegcash field
            if 'gcash' in request.FILES:
                organization.qrcodegcash = request.FILES['gcash']

            # Check and update qrcodepaypal field
            if 'paypal' in request.FILES:
                organization.qrcodepaypal = request.FILES['paypal']

            # Save the organization object to update the database
            organization.save()
            return JsonResponse({'accepted': True})


class OrgClientsPage(LoginRequiredMixin, TemplateView):
    template_name = 'OrgClientsPage.html'

    def get(self,request):
        try:
            user = User.objects.get(email = request.session['username'])
            organization = Organization.objects.get(user=user)
            user_ids = Appointment.objects.filter(appointed_to_id=organization.id, appointmentstatus="accepted").values_list('appointed_by_id', flat=True)
            users = User.objects.filter(id__in=user_ids)
            volunteer_count = get_volunteer_count(request)
            return render(request, 'OrgClientsPage.html', {"users": users, 'volunteer_count':volunteer_count})
        except:
            return render(request, 'OrgHomePage.html', {"error": "You don't have permission to access this web page!"})

    def post(self, request):

        if request.POST.get('pet_id'):
            appointment = Appointment.objects.filter(
                pettobring_id=request.POST['pet_id'],
                petmedicalrecord_id__isnull=True
            ).order_by('appointmentdate').first()
            user_email = request.session.get('username', '')
            user = User.objects.get(email=user_email)
            organization = Organization.objects.get(user=user)
            veterinarians = Veterinarian.objects.filter(organization_id=organization.id)
            data = {'veterinarians': list(veterinarians.values())}
            try:
                appointment_data = {
                    'id': appointment.id,
                    'date': appointment.appointmentdate,
                    'time' : appointment.appointmenttime,
                    'status': appointment.appointmentstatus,
                    'type': appointment.servicetype,
                    'medicine': appointment.petmedicalrecord.medicinename,
                    'note': appointment.petmedicalrecord.note,
                    'vet': appointment.veterinarian.vetname,
                }

            except:
                appointment_data = {
                    'id': appointment.id,
                    'date': appointment.appointmentdate,
                    'time': appointment.appointmenttime,
                    'status': appointment.appointmentstatus,
                    'type': appointment.servicetype,
                }
            try:
                return JsonResponse({'appointment':  appointment_data, 'vet': data})
            except:
                return JsonResponse({'appointment':  appointment_data})
        elif request.POST.get('appointment_id'):
            appointment = Appointment.objects.get(id=request.POST['appointment_id'])
            if request.POST['note'] == "":
                note = ""
            else:
                note = request.POST['note']
            medical_record = PetMedicalRecord.objects.create(medicinename = request.POST['medicine'], note=note)
            medical_record.save()

            appointment.petmedicalrecord_id = medical_record.id
            appointment.veterinarian_id = request.POST['vetname']
            appointment.save()
            return JsonResponse({'isSuccessful': True})
        elif request.POST.get('isAllAppointments'):
            pet = Pets.objects.get(id=request.POST['pet_id_appointment'])
            appointments = Appointment.objects.filter(pettobring_id=request.POST['pet_id_appointment'])
            appointment_list = [
                {
                    'id': appointment.id,
                    'date': appointment.appointmentdate,
                    'diagnosis': appointment.servicetype,
                    'medicine': appointment.petmedicalrecord.medicinename if appointment.petmedicalrecord else "",
                    'veterinarian': appointment.veterinarian.vetname if appointment.veterinarian else "",
                    'note': appointment.petmedicalrecord.note if appointment.petmedicalrecord else "",
                    'clinic': appointment.appointed_to.organization_name
                }
                for appointment in appointments
            ]
            return JsonResponse({'pet_name': pet.pet_name.upper(), 'appointments': appointment_list})
        elif request.POST.get('user_id'):
            if request.POST['isTable'] == "false":
                pet_ids = Appointment.objects.filter(
                    appointed_by_id=request.POST['user_id'],
                    petmedicalrecord_id__isnull=True
                ).values_list('pettobring_id', flat=True)
            else:
                pet_ids = Appointment.objects.filter(appointed_by_id=request.POST['user_id']).values_list('pettobring_id', flat=True)

            pets = Pets.objects.filter(id__in=pet_ids)
            pets_list = [
                {
                    'id': pet.id,
                    'name': pet.pet_name,
                    'age': pet.pet_age,
                    'type': pet.pet_type,
                    'breed': pet.pet_breed,
                    'birthdate': pet.pet_birthdate,
                }
                for pet in pets
            ]
            # Return JSON response
            return JsonResponse({'pets': pets_list})


class OrgVolunteersPage( LoginRequiredMixin, TemplateView):
    template_name = 'OrgVolunteersPage.html'

    def get(self,request):
        try:

            user = User.objects.get(email = request.session['username'])

            organization = Organization.objects.get(user_id = user.id)
            records = VolunteerRecord.objects.filter(org_id = organization.id, volunteerstatus=1)
            volunteer_ids = records.values_list('volunteer_id', flat=True)

            # Filter volunteers based on volunteer_ids
            volunteers = Volunteer.objects.filter(id__in=volunteer_ids)
            volunteer_count = get_volunteer_count(request)

            return render(request, 'OrgVolunteersPage.html', {"volunteers": volunteers, 'volunteer_count': volunteer_count, } )
        except:
            return render(request, 'OrgHomePage.html', {"error": "You don't have permission to access this web page!"})

    def post(self, request):
        user = User.objects.get(email = request.session['username'])
        organization = Organization.objects.get(user_id = user.id)
        if request.POST.get('volunteer_id'):
            volunteer = Volunteer.objects.get(id=request.POST['volunteer_id'])
            email = volunteer.user.email
            if request.POST.get('isAccepted'):
                records = VolunteerRecord.objects.get(volunteer_id=volunteer.id, org_id=organization.id)
                if volunteer.user.usertype == 2:
                    volunteer.user.usertype = 4
                    records.volunteerstatus = 4
                else:
                    volunteer.user.usertype = 6
                    records.volunteerstatus = 6
                volunteer.user.save()
                records.save()
                return JsonResponse({'done': True, 'email':volunteer.user.email, 'org': organization.organization_name})
            elif request.POST.get('isDeclined'):
                records = VolunteerRecord.objects.get(volunteer_id=volunteer.id, org_id=organization.id)
                if volunteer.user.usertype == 5:
                    volunteer.user.usertpe = 1
                    volunteer.user.save()
                records.delete()
                return JsonResponse({'done': True, 'email':email, 'org': organization.organization_name})

            else:
                volunteer_data = {
                    'id': volunteer.id,
                    'firstname': volunteer.user.firstname,
                    'lastname': volunteer.user.lastname,
                    'contactnumber': volunteer.user.contactnumber,
                    'address': volunteer.user.address,
                    'email': volunteer.user.email,
                    'idpicture': volunteer.idpicture.url,
                    'idpictureback': volunteer.idpictureback.url
                }

                return JsonResponse({'volunteer': volunteer_data})
        elif request.POST.get('showAccepted'):
            records = VolunteerRecord.objects.filter(org_id=organization.id, volunteerstatus__in=[4, 6])

            volunteer_ids = records.values_list('volunteer_id', flat=True)

            # Filter volunteers based on volunteer_ids
            volunteers = Volunteer.objects.filter(id__in=volunteer_ids)

            volunteer_data = [
                {
                    'id': volunteer.id,
                    'firstname': volunteer.user.firstname,
                    'lastname': volunteer.user.lastname,
                    'contactnumber': volunteer.user.contactnumber,
                    'address': volunteer.user.address,
                    'email': volunteer.user.email,
                    'idpicture': volunteer.idpicture.url,
                    'idpictureback': volunteer.idpictureback.url
                }
                for volunteer in volunteers
            ]
            return JsonResponse({'volunteers': volunteer_data})


class OrgAppointmentRecsPage( LoginRequiredMixin, TemplateView):
    template_name = 'OrgAppointmentRecsPage.html'
    def get(self,request):
        try:
            user = User.objects.get(email = request.session['username'])
            organization = Organization.objects.get(user_id = user.id)
            records = VolunteerRecord.objects.filter(org_id = organization.id, volunteerstatus=1)
            volunteer_ids = records.values_list('volunteer_id', flat=True)

            # Filter volunteers based on volunteer_ids
            volunteers = Volunteer.objects.filter(id__in=volunteer_ids)
            volunteer_count = get_volunteer_count(request)

            return render(request, 'OrgVolunteersPage.html', {"volunteers": volunteers, 'volunteer_count': volunteer_count, } )
        except:
            return render(request, 'OrgHomePage.html', {"error": "You don't have permission to access this web page!"})

class SystemAdminDashboard(TemplateView):
    template_name = 'SystemAdminDashboard.html'

class SystemAdminHome( LoginRequiredMixin, TemplateView):
    template_name = 'SystemAdminHome.html'

    def get(self,request):
        try:
            user = User.objects.get(email = request.session['username'])
            if user.usertype == 7:
                organizations = Organization.objects.filter(organizationstatus=1)
                return render(request, 'SystemAdminHome.html', {"organizations": organizations})
            else:
                return redirect('/main')
        except Exception as e:
            print(e)
            return redirect('/main')


    def post(self,request):
        if request.POST.get('acceptID'):
            organizations = Organization.objects.get(id = request.POST["acceptID"])
            organizations.organizationstatus=2
            organizations.save()
            return JsonResponse({'accepted': True, 'email': organizations.user.email})
        elif request.POST.get('declineID'):
            organizations = Organization.objects.get(id = request.POST["declineID"])
            email = organizations.user.email
            user_id = organizations.user_id
            organizations.delete()
            user = User.objects.get(id = user_id)
            user.delete()
            return JsonResponse({'declined': True, 'email': email})
        else:
            organization = Organization.objects.get(id = request.POST["orgID"])
            organization_data = {
                'id': organization.id,
                'address': organization.user.address,
                'contactnumber': organization.user.contactnumber,
                'certificate_of_accreditation': organization.certificate_of_accreditation.url if organization.certificate_of_accreditation else None,
                "qrcodebuymeacoffee": organization.qrcodebuymeacoffee.url if organization.qrcodebuymeacoffee else None,
                "qrcodegcash": organization.qrcodegcash.url if organization.qrcodegcash else None,
                "qrcodepaypal": organization.qrcodepaypal.url if organization.qrcodepaypal else None,
            }
            return JsonResponse({'organization': organization_data})



class SystemAdminOrgs( LoginRequiredMixin, TemplateView):
    template_name = 'SystemAdminOrgs.html'

    def get(self,request):
        try:
            user = User.objects.get(email = request.session['username'])
            if user.usertype == 7:
                organizations = Organization.objects.filter(organizationstatus=2)
                return render(request, 'SystemAdminOrgs.html', {"organizations": organizations})
            else:
                return redirect('/main')
        except Exception as e:
            print(e)
            return redirect('/main')


    def post(self,request):
        if request.POST.get('organization_id'):
            organizations = Organization.objects.get(id = request.POST["organization_id"])
            email = organizations.user.email
            user_id = organizations.user_id
            organizations.delete()
            user = User.objects.get(id = user_id)
            user.delete()
            return JsonResponse({'delete': True, 'email':email})
        elif request.POST.get('see_id'):
            organization = Organization.objects.get(id = request.POST["see_id"])
            organization_data = {
                'id': organization.id,
                'address': organization.user.address,
                'contactnumber': organization.user.contactnumber,
                'certificate_of_accreditation': organization.certificate_of_accreditation.url if organization.certificate_of_accreditation else None,
                "qrcodebuymeacoffee": organization.qrcodebuymeacoffee.url if organization.qrcodebuymeacoffee else None,
                "qrcodegcash": organization.qrcodegcash.url if organization.qrcodegcash else None,
                "qrcodepaypal": organization.qrcodepaypal.url if organization.qrcodepaypal else None,
            }
            return JsonResponse({'organization': organization_data})

class SystemAdminLogin(TemplateView):
    template_name = 'SystemAdminLoginPage.html'
    def get(self, request):
        try:
            user = User.objects.create_superuser(email='orcaproject123@gmail.com', password='orca', firstname='admin', lastname='admin', contactnumber=1234567890, address='ateneo', usertype=7)
            user.save()
            return render(request, 'SystemAdminLoginPage.html')
        except Exception as e:
            print(e)
            return render(request, 'SystemAdminLoginPage.html')
    def post(self,request):
        username=request.POST['email']
        password=request.POST['password']
        user = authenticate(request,email=username,password=password)
        if user is not None:
            login(request,user)
            request.session['username'] = username
            request.session.save()
            user = User.objects.get(email = request.session['username'])
            if user.usertype == 7:
                return redirect('/systemadminhome')
            else:
                return redirect('/systemadminlogin')
        else:
            return redirect('/systemadminlogin')