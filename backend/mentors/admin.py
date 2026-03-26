from django.contrib import admin
from .models import MentorApplication, Session, SessionParticipant, MentorRating,CourseMentorRecommendation

admin.site.register(MentorApplication)
admin.site.register(Session)
admin.site.register(SessionParticipant)
admin.site.register(MentorRating)
admin.site.register(CourseMentorRecommendation)
