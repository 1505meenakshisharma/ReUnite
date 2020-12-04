from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from PIL import Image

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    user_mobile_no = PhoneNumberField(max_length = 13, unique = True)
    image = models.ImageField(default = 'default.png', upload_to = 'user_profile_pics')
    class Meta:
        verbose_name_plural = 'User Profile Info'

    def __str__(self):
        return f"(ID = {self.id}) ---> {self.user.username} ' s Profile (ForeignKey User ID = {self.user_id})"

    def save(self):
        super().save()
        img = Image.open(self.image.path)
        if img.width > 225 or img.height > 225:
            output_size = (225, 225)
            img.thumbnail(output_size)
        img.save(self.image.path)

def validate_image_size(image):
    min_size = 1 * 1024 * 1024
    max_size = 5 * 1024 * 1024
    if image.size < min_size or image.size > max_size:
        raise ValidationError("Ensure the size of uploaded image is in the range [ 1 MB - 5 MB ].")
    else:
        return image

class MissingChild(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, null = True)
    full_name = models.CharField(max_length = 60, help_text = "Fullname should be in the format :- First Name Last Name")
    child_aadhar_no = models.BigIntegerField(verbose_name = 'Aadhar no.', blank = True, null = True, validators = [MinValueValidator(200000000000), MaxValueValidator(999999999999)])
    GENDER = (('M', 'Male'), ('F', 'Female'), ('T', 'Transgender'))
    gender = models.CharField(max_length = 1, choices = GENDER, default = None, null = True)
    age = models.PositiveIntegerField(help_text = "Age of the child as of now [ in year(s) ]. Note :- Please don't type the unit i.e., year(s).", validators = [MinValueValidator(1), MaxValueValidator(12)])
    father_name = models.CharField(max_length = 60 ,verbose_name = "Father's name")
    mother_name = models.CharField(max_length = 60 ,verbose_name = "Mother's name")
    nationality = models.CharField(max_length = 60)
    mother_tongue = models.CharField(max_length = 60, blank = True)
    child_image = models.ImageField(upload_to = 'missing_child_images', help_text = "Image must contains front face. It should be in .jpg or .png format having size range [ 1 MB - 5 MB ].", validators = [FileExtensionValidator(allowed_extensions = ['jpg', 'png']), validate_image_size])
    residential_address = models.CharField(max_length = 255, help_text = "Permanent address should be entered containing house no. , road name , village / town name , post office / police station name.")
    district = models.CharField(max_length = 60)
    state = models.CharField(max_length = 30)
    pincode = models.PositiveIntegerField(validators = [MinValueValidator(110001), MaxValueValidator(999999)])
    parent_mobile_no = PhoneNumberField(max_length = 13)
    parent_email = models.EmailField(max_length = 50, blank = True)
    parent_aadhar_no = models.BigIntegerField(validators = [MinValueValidator(200000000000), MaxValueValidator(999999999999)])
    missing_from_place = models.CharField(max_length = 60)
    police_station_nearby_missing_place = models.CharField(max_length = 60)
    missing_from_date = models.DateField()
    missing_from_time = models.TimeField()
    MISSING_CAUSE = (('R', 'Runaway'), ('L', 'Lost'), ('T', 'Trafficked'), ('K', 'Kidnapped'), ('Nl', 'Not listed'))
    missing_cause = models.CharField(max_length = 2, choices = MISSING_CAUSE, default = None, null = True)
    additional_info = models.TextField(max_length = 500, verbose_name = "Detailed Information related to event of Missing (in 500 words)")
    height = models.DecimalField(max_digits = 3, decimal_places = 2, help_text = "Height should be in [ M feet(s) . N inch(es) OR M feet(s) ] format. For example, 4.10 resembles 4 feet 10 inches in our database. Note :- Please don't type the units i.e., feet(s) & inch(es).", validators = [MinValueValidator(2.6), MaxValueValidator(5)])
    weight = models.PositiveIntegerField(help_text = "Weight should be in kg(s) only. Omit the gram(s) if any present. For example, if wish to enter is 21.5 kg(s), just type 21 and omit the decimal part which is in gram(s). Note :- Please don't type the unit i.e., kg(s).", validators = [MinValueValidator(10), MaxValueValidator(80)])
    COMPLEXION = (('D', 'Dark'), ('F', 'Fair'), ('Vf', 'Very fair'))
    complexion = models.CharField(max_length = 2, choices = COMPLEXION, default = None,  null = True)
    BUILD = (('F', 'Fat'), ('N', 'Normal'), ('T', 'Thin'))
    build = models.CharField(max_length = 1, choices = BUILD, default = None,  null = True)
    EYE_COLOR = (('Nm', 'Normal'), ('Bl', 'Blue'), ('Br', 'Brown'), ('R', 'Reddish'), ('G', 'Green'), ('Nl', 'Not listed'))
    eye_color = models.CharField(max_length = 2, choices = EYE_COLOR, default = None,  null = True)
    HAIR_COLOR = (('Br', 'Brown'), ('Cb', 'Curly black'), ('Bl', 'Black'), ('Nl', 'Not listed'))
    hair_color = models.CharField(max_length = 2, choices = HAIR_COLOR, default = None,  null = True)
    upper_wearing_apparel = models.CharField(max_length = 60, verbose_name = "Wearing Upper Apparel", blank = True)
    lower_wearing_apparel = models.CharField(max_length = 60, verbose_name = "Wearing Lower Apparel", blank = True)
    footwear = models.CharField(max_length = 60, blank = True)
    identification_marks = models.CharField(max_length = 100, blank = True)
    DEFORMITIES = (('D', 'Deaf'), ('B', 'Blind'), ('Se', 'Squint eyes'), ('Fe', 'Finger(s) extra'), ('G', 'Goitre'), ('Hm', 'Hand missing'), ('Lm', 'Leg missing'), ('Nl', 'Not listed'))
    deformities = models.CharField(max_length = 2, choices = DEFORMITIES, default = None,  null = True)
    habits = models.CharField(max_length = 100, blank = True)

    class Meta:
        verbose_name_plural = "Missing Child Info"

    def __str__(self):
        return f"(ID = {self.id}) ---> {self.user.username} ' s Child Info (ForeignKey User ID = {self.user_id})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.child_image.path)
        if img.width > 1600 or img.height > 1600:
            output_size = (1600, 1600)
            img.thumbnail(output_size, Image.LANCZOS)
        img.save(self.child_image.path)

class MissingChildEncodedFace(models.Model):
    missing_child = models.OneToOneField(MissingChild, on_delete = models.CASCADE, null = True)
    child_encoded_face = models.BinaryField()

    class Meta:
        verbose_name_plural = "Missing Child Encoded Faces"

    def __str__(self):
        return f"(ID = {self.id}) ---> {self.missing_child.full_name} ' s Encoded Face (ForeignKey Missing Child ID = {self.missing_child_id})"

class SightedChild(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, null = True)
    sighted_child_full_name = models.CharField(max_length = 60, blank = True, verbose_name = "Full name", help_text = "Fullname should be in the format :- First Name Last Name")
    sighted_child_age = models.PositiveIntegerField(verbose_name = "Age", help_text = "Age of the child as of now [ in year(s) ]. Note :- Please don't type the unit i.e., year(s).", validators = [MinValueValidator(1), MaxValueValidator(12)], blank = True, null = True)
    sighted_date = models.DateField()
    sighted_time = models.TimeField()
    sighted_location = models.CharField(max_length = 60)
    sighted_child_image = models.ImageField(upload_to = 'sighted_child_images', help_text = "Image must contains front face. It should be in .jpg or .png format having size range [ 1 MB - 5 MB ].", validators = [FileExtensionValidator(allowed_extensions = ['jpg', 'png']), validate_image_size])
    match_found = models.BooleanField(default = False)

    class Meta:
        verbose_name_plural = "Sighted Child Info"

    def __str__(self):
        return f"(ID = {self.id}) ---> {self.user.username} ' s Child Info (ForeignKey User ID = {self.user_id})"

    def save(self):
        super().save()
        img = Image.open(self.sighted_child_image.path)
        if img.width > 1600 or img.height > 1600:
            output_size = (1600, 1600)
            img.thumbnail(output_size, Image.LANCZOS)
        img.save(self.sighted_child_image.path)
