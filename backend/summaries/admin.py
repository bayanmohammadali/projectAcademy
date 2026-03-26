from django.contrib import admin
from .models import Summary, SummaryVersion, SummaryReview, SummaryRating, Favorite


admin.site.register(Summary)
admin.site.register(SummaryVersion)
admin.site.register(SummaryReview)
admin.site.register(SummaryRating)
admin.site.register(Favorite)
