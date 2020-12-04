from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserProfileForm, UserUpdateForm, ProfileUpdateForm, MissingChildPersonalDetailsForm, MissingChildParentDetailsForm, MissingEventDetailsChildForm, MissingChildPhysicalFeaturesForm, SearchChildForm, SightedChildForm
from .models import MissingChild, MissingChildEncodedFace
from django.core.mail import send_mail
from PIL import Image
import numpy as np, face_recognition, requests, phonenumbers

def homepage(request):
    return render(request, 'homepage.html')

def signup(request):
    if request.method == 'POST':
        r_form = UserRegisterForm(request.POST)
        p_form = UserProfileForm(request.POST)
        if r_form.is_valid() and p_form.is_valid():
            username = r_form.cleaned_data['username']
            instance1 = r_form.save()
            instance2 = p_form.save(commit = False)
            instance2.user = instance1
            instance2.save()
            messages.success(request, f"New account created: {username}, You can login now...")
            return redirect('login')
        else:
            messages.error(request, f"Some error(s) occurred. Please correct the error(s) below.")
    else:
        r_form = UserRegisterForm()
        p_form = UserProfileForm()
    return render(request, 'signup.html', {'r_form': r_form, 'p_form': p_form, 'title': 'Register'})

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance = request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance = request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f"Your account has been updated!")
            return redirect('profile')
        else:
            messages.error(request, f"Some error(s) occurred. Please correct the error(s) below.")
    else:
        u_form = UserUpdateForm(instance = request.user)
        p_form = ProfileUpdateForm(instance = request.user.profile)
    return render(request, 'profile.html', {'u_form': u_form, 'p_form': p_form, 'title': 'Profile'})

@login_required
def missing_child(request):
    if request.method == 'POST':
        per_form = MissingChildPersonalDetailsForm(request.POST, request.FILES)
        par_form = MissingChildParentDetailsForm(request.POST)
        eve_form = MissingEventDetailsChildForm(request.POST)
        phy_form = MissingChildPhysicalFeaturesForm(request.POST)
        if per_form.is_valid() and par_form.is_valid() and eve_form.is_valid() and phy_form.is_valid():
            uploaded_child_image = per_form.cleaned_data.get('child_image')
            child_image = face_recognition.load_image_file(uploaded_child_image)
            if max(child_image.shape) > 1600:
                img = Image.fromarray(child_image)
                img.thumbnail((1600, 1600), Image.LANCZOS)
                child_image = np.array(img)
            child_face_encoding = face_recognition.face_encodings(child_image)
            if len(child_face_encoding) == 0:
                messages.error(request, f"No face(s) recognized in the uploaded image!!! Please upload a clear version of the same image or a different one.")
            elif len(child_face_encoding) > 1:
                messages.error(request, f"More than one face recognized in the uploaded image!!! Please upload an image having single face of the missing child to avoid ambiguity.")
            else:
                form_list = [per_form, par_form, eve_form, phy_form]
                data = {k: v for form in form_list for k, v in form.cleaned_data.items()}
                instance1 = MissingChild.objects.create(**data) # creating an object of MissingChild model using
                                                                # kwargs (keyword arguments) **data in dictionary format
                instance1.user = request.user
                instance1.gender = instance1.get_gender_display()
                instance1.missing_cause = instance1.get_missing_cause_display()
                instance1.complexion = instance1.get_complexion_display()
                instance1.build = instance1.get_build_display()
                instance1.eye_color = instance1.get_eye_color_display()
                instance1.hair_color = instance1.get_hair_color_display()
                instance1.deformities = instance1.get_deformities_display()
                instance1.save()
                child_face_encoding_in_bytecode = child_face_encoding[0].tostring()
                instance2 = MissingChildEncodedFace.objects.create(child_encoded_face = child_face_encoding_in_bytecode)
                instance2.missing_child = instance1
                instance2.save()
                messages.success(request, f"Missing Child details submitted successfully...")
                return redirect('missing_child')
        else:
            messages.error(request, f"Some error(s) occurred. Please correct the error(s) below.")
    else:
        per_form = MissingChildPersonalDetailsForm()
        par_form = MissingChildParentDetailsForm()
        eve_form = MissingEventDetailsChildForm()
        phy_form = MissingChildPhysicalFeaturesForm()
    return render(request, 'missing_child.html', {'per_form': per_form, 'par_form': par_form, 'eve_form': eve_form, 'phy_form': phy_form, 'title': 'Missing Child'})

def face_comparision(request, child_image_to_search):
    unknown_image = face_recognition.load_image_file(child_image_to_search)
    if max(unknown_image.shape) > 1600:
        img = Image.fromarray(unknown_image)
        img.thumbnail((1600, 1600), Image.LANCZOS)
        unknown_image = np.array(img)
    unknown_face_encoding = face_recognition.face_encodings(unknown_image)
    if len(unknown_face_encoding) == 0:
        messages.error(request, f"No face(s) recognized in the uploaded image!!! Please upload a clear version of the same image or a different one.")
    elif len(unknown_face_encoding) > 1:
        messages.error(request, f"More than one face recognized in the uploaded image!!! Please upload an image having single face of the missing child to avoid ambiguity.")
    else:
        unknown_face_encoding = unknown_face_encoding[0]
        encodings = MissingChildEncodedFace.objects.all()
        search_results = []
        for encoding in encodings:
            known_face_encoding = np.fromstring(encoding.child_encoded_face)
            results = face_recognition.compare_faces([known_face_encoding], unknown_face_encoding)
            if results[0]:
                corresponding_missing_child_object = MissingChild.objects.get(pk = encoding.missing_child_id)
                search_results.append(corresponding_missing_child_object)
        return search_results

res = None
class_name = ""
@login_required
def search_child(request, pk = None):
    if request.method == 'POST':
        global res
        global class_name
        res = None
        class_name = ""
        search_form = SearchChildForm(request.POST, request.FILES)
        if search_form.is_valid():
            full_name_to_search = search_form.cleaned_data['full_name_to_search']
            child_image_to_search = search_form.cleaned_data['child_image_to_search']
            if full_name_to_search == "" and child_image_to_search == None:
                messages.error(request, f"Access Denied!!! Please fill any one field.")
            else:
                if full_name_to_search != "" and child_image_to_search == None:
                    res = MissingChild.objects.filter(full_name__iexact = full_name_to_search) # field_name__iexact
                                                                                               # for Case-insensitive
                                                                                               # exact match
                    class_name = res.__class__.__name__
                elif full_name_to_search == "" and child_image_to_search != None:
                    res = face_comparision(request, child_image_to_search)
                    class_name = res.__class__.__name__
                else:
                    full_name_res = list(MissingChild.objects.filter(full_name__iexact = full_name_to_search))
                    child_image_res = face_comparision(request, child_image_to_search)
                    if child_image_res.__class__.__name__ == "list":
                        res = []
                        class_name = res.__class__.__name__
                    if full_name_res and child_image_res:
                        res = [query_res for query_res in full_name_res if query_res in child_image_res]
                        class_name = res.__class__.__name__
                search_form = SearchChildForm()
                return render(request, 'search_child.html', {'search_form': search_form, 'res': res, 'class_name': class_name, 'title' : 'Search Results'})
        else:
            messages.error(request, f"Some error(s) occurred. Please correct the error(s) below.")
    else:
        search_form = SearchChildForm()
        if pk:
            clicked_user = MissingChild.objects.get(pk = pk)
            return render(request, 'search_child.html', {'search_form': search_form, 'res': res, 'class_name': class_name, 'clicked_user': clicked_user, 'title': 'Search Results'})
    return render(request, 'search_child.html', {'search_form': search_form, 'title': 'Search Child'})

@login_required
def sighted_child(request):
    if request.method == 'POST':
        sighted_form = SightedChildForm(request.POST, request.FILES)
        if sighted_form.is_valid():
            sighted_child_full_name = sighted_form.cleaned_data['sighted_child_full_name']
            sighted_child_age = sighted_form.cleaned_data['sighted_child_age']
            sighted_date = sighted_form.cleaned_data['sighted_date']
            sighted_time = sighted_form.cleaned_data['sighted_time']
            sighted_location = sighted_form.cleaned_data['sighted_location']
            sighted_child_image = sighted_form.cleaned_data['sighted_child_image']
            result = face_comparision(request, sighted_child_image)
            if result:
                url = "https://www.fast2sms.com/dev/bulk"
                headers = {
                    'authorization': "Your API authorization key of Fast2SMS account",
                    'Content-Type': "application/x-www-form-urlencoded",
                    'Cache-Control': "no-cache",
                    }
                for matched_child in result:
                    mail_msg = f"Hi {matched_child.user.first_name},\n\nYour missing child {matched_child.full_name} is sighted at {sighted_location} on {sighted_date.strftime('%d-%b-%Y')} {sighted_time.strftime('%I:%M %p')}. Your child has been sighted by {request.user.first_name}. Our website uses Face Recognition as Image Processing technique to compare between two faces i.e., between a sighted child image & list of all missing child images stored on our server's database. Face Recognition algorithm is triggered on our website as soon as Sighted Child form is submitted with an image of sighted child.\n\nYou've got this notification mail because your missing child's face is most probably matching with the sighted child's face uploaded by {request.user.first_name} through Sighted Child form on our website. Our team is trying its best to provide all the details of sighted user ({request.user.first_name}) as well as sighted child matched with your missing child.\n\nThe team is sharing some of the basic details of {request.user.first_name} which can be used for any sort of further communication for gaining detailed information about the sighted events.\n\nBasic details of {request.user.first_name} (Sighted User) are :-\n\nFull Name : {request.user.first_name} {request.user.last_name}\nEmail : {request.user.email}\nMobile No. : {request.user.profile.user_mobile_no}\n\nSighted Child details are :-\n\nFull Name : {sighted_child_full_name}            (This field can be empty when sighted user doesn't know the sighted child's name.)\nAge :           {sighted_child_age} yr.                 (This field can be None when sighted user doesn't know the sighted child's age.)\nSighted Date : {sighted_date.strftime('%d-%b-%Y')}\nSighted Time : {sighted_time.strftime('%I:%M %p')}\nSighted Location : {sighted_location}\n\nThanks & Regards,\nReUnite Team"

                    sms_msg = f"Hi {matched_child.user.first_name},\n\nYour missing child {matched_child.full_name} is sighted at {sighted_location} on {sighted_date.strftime('%d-%b-%Y')} {sighted_time.strftime('%I:%M %p')}. An email has been sent to your registered Email ID for detailed information about sighted child as well as sighted user.\n\nThanks and Regards,\nReUnite Team"

                    x = phonenumbers.parse(f"{matched_child.user.profile.user_mobile_no}")
                    user_mobile_no_with_country_prefix_code_0 = str(phonenumbers.format_number(x, phonenumbers.PhoneNumberFormat.NATIONAL)).replace(" ", "")
                    user_mobile_no_without_country_prefix_code = int(user_mobile_no_with_country_prefix_code_0[1:])

                    send_mail(
                        subject = "Greetings, your missing child has been sighted by someone...",
                        message = mail_msg,
                        from_email = "ReUnite Team",
                        recipient_list = [matched_child.user.email]
                    )
                    payload = f"sender_id=FSTSMS&message={sms_msg}&language=english&route=p&numbers={user_mobile_no_without_country_prefix_code}"
                    requests.request("POST", url, data = payload, headers = headers)
            instance = sighted_form.save(commit = False)
            instance.user = request.user
            if result:
                instance.match_found = True
                instance.save()
                messages.success(request, f"{len(result)} match(es) found. Sighted Child details submitted successfully. Email & SMS have been sent to all matched cases.")
            else:
                instance.save()
                messages.error(request, f"No match found. But the details have been saved successfully for mapping with future missing child cases.")
            sighted_form = SightedChildForm()
            return render(request, 'sighted_child.html', {'sighted_form': sighted_form, 'title' : 'Sighted Results'})
        else:
            messages.error(request, f"Some error(s) occurred. Please correct the error(s) below.")
    else:
        sighted_form = SightedChildForm()
    return render(request, 'sighted_child.html', {'sighted_form': sighted_form, 'title': 'Sighted Child'})

def about(request):
    return render(request, 'about.html', {'title': 'About'})
