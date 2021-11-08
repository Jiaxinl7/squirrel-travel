from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('search/place/<int:pid>/', views.place, name = 'place'),
    path('search/restaurant/<slug:rid>/', views.restaurant, name = 'restaurant')
]