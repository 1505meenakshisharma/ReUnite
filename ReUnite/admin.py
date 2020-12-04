from django.contrib import admin
from .models import Profile, MissingChild, MissingChildEncodedFace, SightedChild

admin.site.register(Profile)
admin.site.register(MissingChild)
admin.site.register(MissingChildEncodedFace)
admin.site.register(SightedChild)
