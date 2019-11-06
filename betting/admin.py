from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Competition)
admin.site.register(Club)
admin.site.register(Competitor)
# admin.site.register(Team)
admin.site.register(BetPlacing)
admin.site.register(MarketPlacing)
# admin.site.register(Market)
admin.site.register(Punter)
# admin.site.register(Bet)
admin.site.register(Result)