from typing import Coroutine
from django.db.models.aggregates import Count
from django.shortcuts import render
from django.http import HttpResponse, request
from .models import City, Place, NRestaurant, Event
from timeline.models import Visit, Dine
from user.models import User
from django.db import models
from django.db.models.aggregates import Avg, Count
from django.db.models import F, OuterRef, Subquery, Exists


def index(request):
    # return HttpResponse("Here is the manager page.")
    print('index page:')
    request.session['is_login'] = True
    request.session['user_id'] = 2
    request.session['user_name'] = 'aaa'
    return render(request, 'manager/index.html')

def search(request):
    print('search page:',request.GET['city'])
    date = request.GET['date']
    cid = City.objects.get(c_name = request.GET['city'])
    place = Place.objects.filter(cid = cid).order_by('p_name')
    restaurant = NRestaurant.objects.filter(cid = cid).order_by('r_name')
    # visit = Visit.objects.filter(date = date).order_by('start_time')
    # dine = Dine.objects.filter(date = date).order_by('start_time')
    visit = Visit.objects.select_related('pid').filter(date=date)
    visit = [[v.start_time, v.end_time, v.pid.p_name, v.pid.location, v.vid, 'v'] for v in visit]
    dine = Dine.objects.select_related('rid').filter(date=date)
    dine = [[d.start_time, d.end_time, d.rid.r_name, d.rid.r_address, d.did, 'd'] for d in dine]
    destination = sorted(visit + dine)
    print(destination)

    print('cid', cid)
    print('num of place:', len(place))
    print('num of restaurant:', len(restaurant))
    # print('num of visit:', len(visit))
    # print('num of dine:', len(dine))

    # request.session['user_id'] = 1
    return render(request, 'manager/display.html', {'date': date, 'place': place, 'restaurant': restaurant, 'destination': destination})

def place(request, pid):
    print('place page:')
    place = Place.objects.get(pid = pid)
    events = Event.objects.filter(pid = pid).order_by('start_date')
    print(place.p_name,' event:', len(events))
    # create visit
    if request.method == 'POST':
        date = request.POST['date']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']
        user = User.objects.get(uid = request.session['user_id'])
        visit_instance = Visit.objects.create(uid = user, pid = place, date = date, start_time = start_time, end_time = end_time)
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


def restaurant(request, rid):
    print('restaurant page:')
    restaurant = NRestaurant.objects.get(id = rid)
    # create dine
    if request.method == 'POST':
        date = request.POST['date']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']
        user = User.objects.get(uid = request.session['user_id'])
        Dine_instance = Dine.objects.create(uid = user, rid = restaurant, date = date, start_time = start_time, end_time = end_time)
        return render(request, 'manager/restaurant.html', 
        {'restaurant': restaurant, 'date': date, 'start_time': start_time, 'end_time': end_time})
    # display restaurant
    return render(request, 'manager/restaurant.html', {'restaurant': restaurant})

def delete_visit(request, vid):
    # print(request)

    Visit.objects.filter(vid=vid).delete()

    return render(request, 'manager/index.html')

def edit_visit(request,vid):
    visit = Visit.objects.filter(vid=vid).first()
    if request.method == 'POST':
        date = request.POST['date']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']
        user = User.objects.get(uid = request.session['user_id'])
        Visit.objects.filter(vid=vid).update( date = date, start_time = start_time, end_time = end_time)
        return render(request, 'manager/index.html')
    return render(request, 'manager/edit_visit.html')

def delete_dine(request, did):
    # print(request)

    Dine.objects.filter(did=did).delete()

    return render(request, 'manager/index.html')

def edit_dine(request,did):
    dine = Dine.objects.filter(did=did).first()
    if request.method == 'POST':
        date = request.POST['date']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']
        user = User.objects.get(uid = request.session['user_id'])
        Dine.objects.filter(did=did).update( date = date, start_time = start_time, end_time = end_time)
        return render(request, 'manager/index.html')
    return render(request, 'manager/edit_dine.html')