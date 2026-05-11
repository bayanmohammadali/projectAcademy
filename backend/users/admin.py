from django.contrib import admin
from .models import User, Notification, Survey, SurveyQuestion, SurveyAnswer 

admin.site.register(User)
admin.site.register(Notification)   
admin.site.register(Survey)
admin.site.register(SurveyQuestion)
admin.site.register(SurveyAnswer)