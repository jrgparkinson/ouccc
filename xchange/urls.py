# from django.conf.urls import include, url
# from django.contrib import admin
from xchange import views
# from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path

# For namespacing
app_name = 'xchange'

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('trades/', views.trades, name='trades'),
    path('incoming_trades/', views.incoming_trades, name='incoming_trades'),
    path('past_trades/', views.past_trades, name='past_trades'),
    path('make_trade/', views.make_trade, name='make_trade'),
    path('create_trade/', views.create_trade, name='create_trade'),
    path('respond_to_trade/', views.respond_to_trade, name='respond_to_trade'),
    path('respond_to_open_trade/', views.respond_to_open_trade, name='respond_to_open_trade'),
    path('marketplace/', views.marketplace, name='marketplace'),
    path('marketplace_selling/', views.marketplace_selling, name='marketplace_selling'),
    path('marketplace_buying/', views.marketplace_buying, name='marketplace_buying'),
    path('get_investors_for_runner/', views.get_investors_for_runner, name='get_investors_for_runner'),
]


#path('register/', views.register, name='register'),
    #path('login/', auth_views.login, {'template_name': 'login.html'}, name='login'),
    #path('login/', views.login, name='login'),
    #path('logout/', views.logout, name='logout'),
    #path('logout/', 'django.contrib.authviews.logout', {'next_page': '/'}),


# admin.autodiscover()

#urlpatterns = patterns('',
 #   .......
#) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urlpatterns += staticfiles_urlpatterns()
