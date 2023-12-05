from django.db import models
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

class MyUserManager(BaseUserManager):
    def create_user(self, firstname, lastname, contactnumber, address, email, usertype, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        user = self.model(firstname=firstname, lastname=lastname, contactnumber=contactnumber, address=address, email=email, usertype=usertype, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, firstname, lastname, contactnumber, address, email, usertype, password,  **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(firstname, lastname, contactnumber, address, email,  usertype, password=password, **extra_fields)


# Create your models here.

class User(AbstractBaseUser, PermissionsMixin):
    userphoto = models.ImageField(upload_to='images/userprofiles', default = "",  null=True, blank=True)
    firstname = models.CharField(max_length=50, verbose_name="firstname")
    lastname = models.CharField(max_length=50, verbose_name="lastname")
    contactnumber = models.CharField(max_length=11, unique=True, verbose_name="contactnumber")
    address = models.CharField(max_length=100, verbose_name="address")
    email = models.CharField(max_length=100, unique=True, verbose_name="email")
    usertype = models.IntegerField(default = 1, verbose_name="usertype")
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    objects = MyUserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        db_table = "users"

class Organization(models.Model):
    organization_name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    cliniclogo = models.ImageField(upload_to='images/logo')
    qrcodebuymeacoffee = models.ImageField(upload_to='images/qrcodesbuymeacoffee')
    qrcodegcash = models.ImageField(upload_to='images/qrcodesgcash')
    qrcodepaypal = models.ImageField(upload_to='images/qrcodespaypal')
    certificate_of_accreditation = models.FileField(upload_to='pdfs/certificates')
    organizationstatus = models.IntegerField(default = 1)
    class Meta:
       db_table = "organization"

class BusinessHours(models.Model):
    DAY_CHOICES = [
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='business_hours')
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    open_time = models.TimeField()
    close_time = models.TimeField()
    class Meta:
        db_table = "businesshours"

class AppointmentTime(models.Model):
    appointment_time = models.TimeField()
    businesshours = models.ForeignKey(BusinessHours, on_delete = models.CASCADE)

    class Meta:
        db_table = "appointmenttime"


class Services(models.Model):
    organization = models.ForeignKey(Organization, on_delete = models.CASCADE)
    service_offered = models.CharField(max_length=100)
    duration = models.IntegerField()
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = "services"

class Volunteer(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    idpicture = models.ImageField(upload_to='images/volunteerpictures')
    idpictureback = models.ImageField(upload_to='images/volunteerpicturesback')
    class Meta:
        db_table = "volunteers"

class Highlights(models.Model):
    volunteer = models.ForeignKey(Volunteer, on_delete = models.CASCADE)
    highlightstitle = models.CharField(max_length=50)
    highlightsphoto = models.ImageField(upload_to='images/volunteerimgposts')
    highlightsdescription= models.CharField(max_length=500)
    class Meta:
       db_table = "highlights"

class Veterinarian(models.Model):
    organization = models.ForeignKey(Organization, on_delete = models.CASCADE)
    profilepicture = models.ImageField(upload_to='images/vetphoto')
    vetname = models.CharField(max_length=50)
    vetdescription = models.CharField(max_length=500)
    class Meta:
       db_table = "veterinarian"

class Pets(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    pet_picture = models.ImageField(upload_to='images/petpics')
    pet_name = models.CharField(max_length=50)
    pet_type = models.CharField(max_length=5)
    pet_breed = models.CharField(max_length=150)
    pet_birthdate = models.DateTimeField()
    pet_age = models.CharField(max_length=50)
    pet_gender = models.CharField(max_length=10)
    class Meta:
       db_table = "pets"

class PetBreed(models.Model):
    pet_breed = models.CharField(unique=True, max_length=150)
    pet_type = models.CharField(max_length=5)
    class Meta:
        db_table = "petbreed"

class PetMedicalRecord(models.Model):
    medicinename = models.CharField(max_length=150)
    note = models.CharField(max_length=150, default="", null=True, blank=True)
    class Meta:
       db_table = "petmedicalrecord"

class Appointment(models.Model):
    appointed_to = models.ForeignKey(Organization, on_delete = models.CASCADE)
    appointmentdate = models.DateField()
    appointmenttime = models.TimeField()
    servicetype = models.CharField(max_length=100)
    pettobring = models.ForeignKey(Pets, on_delete = models.CASCADE)
    petmedicalrecord = models.ForeignKey(PetMedicalRecord, on_delete = models.CASCADE, default="", null=True, blank=True,)
    veterinarian = models.ForeignKey(Veterinarian, on_delete = models.CASCADE, default="", null=True, blank=True,)
    appointmentstatus = models.CharField(max_length=10, default="pending")
    appointed_by = models.ForeignKey(User, on_delete = models.CASCADE)
    class Meta:
       db_table = "appointment"

class VolunteerRecord(models.Model):
    dateapproved = models.DateTimeField()
    volunteerstatus = models.IntegerField(default = 1)
    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE)
    org = models.ForeignKey(Organization, on_delete=models.CASCADE)
    class Meta:
       db_table = "volunteerrecord"

class AppointmentRecord(models.Model):
    dateapproved = models.DateTimeField()
    appointmentstatus = models.IntegerField(default = 1)
    class Meta:
       db_table = "appointmentrecord"
