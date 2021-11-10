from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('recom/', views.recommend, name='recommend'),
    path('search/', views.search, name='search'),
<<<<<<< HEAD
    path('search/place/<int:pid>/', views.place, name = 'place')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
=======
    path('search/place/<int:pid>/', views.place, name = 'place'),
    path('search/restaurant/<slug:rid>/', views.restaurant, name = 'restaurant')
]
>>>>>>> 38b6cf3e68e3bbdf3f2fcf1a76c62da7ce5555ec
