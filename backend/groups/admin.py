from django.contrib import admin
from .models import StudyGroup, GroupMember, GroupMessage, GroupFile

admin.site.register(StudyGroup)
admin.site.register(GroupMember)
admin.site.register(GroupMessage)
admin.site.register(GroupFile)