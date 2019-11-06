from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('market/<int:id>/', views.market),
    path('placeBet/<int:market_id>/', views.place_bet),
    ]