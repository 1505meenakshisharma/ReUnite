from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, MissingChild, SightedChild
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

class DateInput(forms.DateInput):
    input_type = 'date'

class TimeInput(forms.TimeInput):
    input_type = 'time'

class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length = 30)
    last_name = forms.CharField(max_length = 30)
    email = forms.EmailField(max_length = 50)
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        domain = email.split('@')[1]
        domain_list = ['gmail.com', 'yahoo.com', 'hotmail.com']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Profile with this Email address already exists.")
        if domain not in domain_list:
            raise forms.ValidationError("Enter an Email address with a valid domain. Valid domains are ['gmail.com', 'yahoo.com', 'hotmail.com']")
        return email

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['user_mobile_no']
        widgets = {'user_mobile_no' : PhoneNumberPrefixWidget(attrs = {'onkeypress': 'if(this.value.length === 10) event.preventDefault()'})}

class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length = 30)
    last_name = forms.CharField(max_length = 30)
    email = forms.EmailField(max_length = 50)
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        domain = email.split('@')[1]
        domain_list = ['gmail.com', 'yahoo.com', 'hotmail.com']
        if User.objects.filter(email=email).exists() and self.instance.email != email:
            raise forms.ValidationError("Profile with this Email address already exists.")
        if domain not in domain_list:
            raise forms.ValidationError("Enter an Email address with a valid domain. Valid domains are ['gmail.com', 'yahoo.com', 'hotmail.com']")
        return email

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['user_mobile_no', 'image']
        widgets = {'user_mobile_no' : PhoneNumberPrefixWidget(attrs = {'onkeypress': 'if(this.value.length === 10) event.preventDefault()'})}

class MissingChildPersonalDetailsForm(forms.ModelForm):
    class Meta:
        model = MissingChild
        fields = ['full_name', 'child_aadhar_no', 'gender', 'age', 'father_name', 'mother_name', 'nationality',
                  'mother_tongue', 'child_image']
        widgets = {'gender': forms.Select,
                   'child_aadhar_no': forms.NumberInput(attrs = {'onkeypress': 'if(this.value.length === 12) event.preventDefault()'}),
                   'age': forms.NumberInput(attrs = {'onkeypress': 'if(this.value.length === 2) event.preventDefault()'})
                  }

class MissingChildParentDetailsForm(forms.ModelForm):
    class Meta:
        model = MissingChild
        fields = ['residential_address', 'district', 'state', 'pincode', 'parent_mobile_no', 'parent_email',
                  'parent_aadhar_no']
        widgets = {'pincode': forms.NumberInput(attrs = {'onkeypress': 'if(this.value.length === 6) event.preventDefault()'}),
                   'parent_mobile_no' : PhoneNumberPrefixWidget(attrs = {'onkeypress': 'if(this.value.length === 10) event.preventDefault()'}),
                   'parent_aadhar_no': forms.NumberInput(attrs = {'onkeypress': 'if(this.value.length === 12) event.preventDefault()'})
                  }

class MissingEventDetailsChildForm(forms.ModelForm):
    missing_from_date = forms.DateField(label = 'Date of missing',
                                        help_text = "Date should be in YYYY-MM-DD format , if datepicker widget will not work. If the datepicker widget works, format would be DD-MMM-YYYY automatically.",
                                        widget = DateInput)
    missing_from_time = forms.TimeField(label = 'Time of missing',
                                        help_text = "Time should be in HH:MM:SS format , if timepicker widget will not work. If the timepicker widget works, format would be HH:MM AM/PM ( 12-hour clock [ 12:00 AM - 11:59 PM ] ) automatically.",
                                        widget = TimeInput)
    class Meta:
        model = MissingChild
        fields = ['missing_from_place', 'police_station_nearby_missing_place', 'missing_from_date', 'missing_from_time',
                  'missing_cause', 'additional_info']
        widgets = {'missing_cause': forms.Select}

class MissingChildPhysicalFeaturesForm(forms.ModelForm):
    class Meta:
        model = MissingChild
        fields = ['height', 'weight', 'complexion', 'build', 'eye_color', 'hair_color', 'upper_wearing_apparel',
                  'lower_wearing_apparel', 'footwear', 'identification_marks', 'deformities', 'habits']
        widgets = {'complexion': forms.Select,
                   'build': forms.Select,
                   'eye_color': forms.Select,
                   'hair_color': forms.Select,
                   'deformities': forms.Select,
                   'height': forms.NumberInput(attrs = {'onkeypress': 'if(this.value.length === 4) event.preventDefault()'}),
                   'weight': forms.NumberInput(attrs = {'onkeypress': 'if(this.value.length === 3) event.preventDefault()'})
                   }

def validate_image_size(image):
    min_size = 1 * 1024 * 1024
    max_size = 5 * 1024 * 1024
    if image.size < min_size or image.size > max_size:
        raise ValidationError("Ensure the size of uploaded image is in the range [ 1 MB - 5 MB ].")
    else:
        return image

class SearchChildForm(forms.Form):
    full_name_to_search = forms.CharField(max_length = 60, required = False, help_text = "Fullname should be in the format :- First Name Last Name")
    child_image_to_search = forms.ImageField(required = False, help_text = "Image must contains front face. It should be in .jpg or .png format having size range [ 1 MB - 5 MB ].", validators = [FileExtensionValidator(allowed_extensions = ['jpg', 'png']), validate_image_size])

class SightedChildForm(forms.ModelForm):
    sighted_date = forms.DateField(help_text = "Date should be in YYYY-MM-DD format , if datepicker widget will not work. If the datepicker widget works, format would be DD-MMM-YYYY automatically.",
                                   widget = DateInput)
    sighted_time = forms.TimeField(help_text = "Time should be in HH:MM:SS format , if timepicker widget will not work. If the timepicker widget works, format would be HH:MM AM/PM ( 12-hour clock [ 12:00 AM - 11:59 PM ] ) automatically.",
                                   widget = TimeInput)
    class Meta:
        model = SightedChild
        fields = ['sighted_child_full_name', 'sighted_child_age', 'sighted_date', 'sighted_time', 'sighted_location', 'sighted_child_image']
