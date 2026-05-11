from django.contrib import admin
from .models import MentorApplication,MentorRating,CourseMentorRecommendation, ChatRoom, ChatMessage, MentorRenewal

admin.site.register(MentorApplication)
admin.site.register(MentorRating)
admin.site.register(CourseMentorRecommendation)
admin.site.register(ChatRoom)
admin.site.register(ChatMessage)
admin.site.register(MentorRenewal)
