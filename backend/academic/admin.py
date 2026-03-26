from django.contrib import admin
from .models import University, AcademicYear, Semester

admin.site.register(University)
admin.site.register(AcademicYear)
admin.site.register(Semester)