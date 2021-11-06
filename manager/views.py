from django.shortcuts import render
from django.http import HttpResponse
from .models import City, Place, NRestaurant


def index(request):
    # return HttpResponse("Here is the manager page.")
    print('index page:')
    return render(request, 'manager/index.html')

def search(request):
    print('search page:')
    print(request.GET['date'])
    print(request.GET['city'])
    cid = City.objects.get(c_name = request.GET['city'])
    place = Place.objects.filter(cid = cid).order_by('p_name')
    restaurant = NRestaurant.objects.filter(cid = cid).order_by('r_name')

    print('cid', cid)
    print('num of place:', len(place))
    print('num of restaurant:', len(restaurant))
    # return HttpResponse("Here is the manager page.")
    return render(request, 'manager/display.html', {'place': place, 'restaurant': restaurant})