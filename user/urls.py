# mysite_login/urls.py

from django.urls.conf import path, include
from user import views


urlpatterns = [
    path('index/', views.index),
    path('login/', views.login),
    path('register/', views.register),
    path('logout/', views.logout),
    path('captcha/', include('captcha.urls')),
]