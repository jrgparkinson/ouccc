from django.contrib import admin
from .models import Share, Runner, Trade, Dividend
# Register your models here.

admin.site.register(Share)
admin.site.register(Runner)
admin.site.register(Trade)
admin.site.register(Dividend)