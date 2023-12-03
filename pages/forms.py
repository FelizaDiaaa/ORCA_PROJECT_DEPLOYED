from django import forms 
from django.forms import ModelForm
from .models import User

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['firstname', 'lastname', 'contactnumber', 'email']