from django.contrib import admin
from .models import Group, GroupMember, GroupMessage, GroupFile

admin.site.register(Group)
admin.site.register(GroupMember)
admin.site.register(GroupMessage)
admin.site.register(GroupFile)