from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('recom/', views.recommend, name='recommend'),
    path('search/', views.search, name='search'),
    path('search/place/<int:pid>/', views.place, name = 'place')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)