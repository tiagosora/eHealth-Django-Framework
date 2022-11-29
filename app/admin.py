from django.contrib import admin
from app.models import *

# Register your models here.
admin.site.register(Patient)
admin.site.register(Department)
admin.site.register(Appointment)