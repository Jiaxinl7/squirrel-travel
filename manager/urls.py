from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('recom/', views.recommend, name='recommend'),
    path('search/', views.search, name='search'),
    path('search/place/<int:pid>/', views.place, name = 'place')
    path('search/place/<int:pid>/', views.place, name = 'place'),
    path('search/restaurant/<slug:rid>/', views.restaurant, name = 'restaurant'),
    path('search/delete_visit/<int:vid>/', views.delete_visit, name='delete_visit'),
    path('search/edit_visit/<int:vid>/', views.edit_visit, name='edit_visit')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

