from typing import Coroutine
from django.db.models.aggregates import Count
from django.shortcuts import render
from django.http import HttpResponse, request
from .models import City, Place, NRestaurant, Event
from timeline.models import Visit
from django.db import models
from django.db.models.aggregates import Avg, Count
from django.db.models import F, OuterRef, Subquery, Exists


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
    print('session:', list(request.session.keys()))
    # request.session['user_id'] = 1
    return render(request, 'manager/display.html', {'place': place, 'restaurant': restaurant})

def place(request, pid):
    print('place page:')
    place = Place.objects.get(pid = pid)
    events = Event.objects.filter(pid = pid).order_by('start_date')
    print(place.p_name,' event:', len(events))
    if request.method == 'POST':
        date = request.POST['date']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']

        visit_instance = Visit.objects.create(uid = request.session['user_id'], pid = place.pid, date = date, start_time = start_time, end_time = end_time)
        return render(request, 'manager/place.html', 
        {'place': place, 'events': events, 'date': date, 'start_time': start_time, 'end_time': end_time})
    return render(request, 'manager/place.html', {'place': place, 'events': events})



def recommend(request):
    # Treasure restaurants you may not find yet
    rec_list = NRestaurant.objects.values('categories').annotate(avgcount=Avg('review_count')).filter(review_count__lte=F('avgcount'),stars__gte=4).values('categories','r_name','r_address')[:15]
    print(rec_list)
    

    # Cities that hold lots of events recently
    queryset = Place.objects.select_related('event', 'city').values('cid').annotate(c=Count('event')).order_by('-c')[:15]
    cnames = City.objects.filter(cid__in=[queryset[i]['cid'] for i in range(len(queryset))]).values('c_name')
    return render(request, 'manager/advancedquery.html', {'rec_list': rec_list, 'cnames': cnames})