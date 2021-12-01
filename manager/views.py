from django.db.models.aggregates import Count
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .models import City, Place, NRestaurant, Event
from timeline.models import Visit, Dine
from user.models import User
from django.db import models, connection
from django.db.models.aggregates import Avg, Count
import datetime


def index(request):
    # return HttpResponse("Here is the manager page.")
    print('index page:')
    # request.session['is_login'] = True
    # request.session['user_id'] = 2
    # request.session['user_name'] = 'aaa'
    return render(request, 'manager/index.html')

def search(request):
    print('search page:',request.GET['city'])
    date = request.GET['date']
    # cid = City.objects.get(c_name = request.GET['city'])
    city = City.objects.raw('SELECT * FROM city WHERE c_name=%s',[request.GET['city']])[0]
    cid = city.cid
    # place = Place.objects.filter(cid = cid).order_by('p_name')
    place = Place.objects.raw('SELECT * FROM Place WHERE cid = %s ORDER BY p_name', [cid])
    # restaurant = NRestaurant.objects.filter(cid = cid).order_by('r_name')
    restaurant = NRestaurant.objects.raw('SELECT * FROM n_restaurant WHERE cid = %s ORDER BY r_name', [cid])

    # visit = Visit.objects.select_related('pid').filter(date=date)
    with connection.cursor() as cursor:
        cursor.execute("SELECT start_time, end_time, p_name, location, vid FROM visit NATURAL JOIN place WHERE date = %s and uid = %s", [date, request.session['user_id']])
        visit = cursor.fetchall()
    visit = [[v[0], v[1], v[2], v[3], v[4], 1] for v in visit]
    print('len of visit:', len(visit))

    # dine = Dine.objects.select_related('rid').filter(date=date)
    with connection.cursor() as cursor:
        cursor.execute("SELECT start_time, end_time, r_name, r_address, did FROM dine JOIN n_restaurant on dine.rid = n_restaurant.id WHERE date = %s and uid = %s", [date, request.session['user_id']])
        dine = cursor.fetchall()
    dine = [[d[0], d[1], d[2], d[3], d[4], 0] for d in dine]
    
    print('len of dine:', len(dine))
    destination = sorted(visit + dine)
    # print('destination', destination)

    print('cid', cid)
    print('num of place:', len(place))
    print('num of restaurant:', len(restaurant))
    # print('num of visit:', len(visit))
    # print('num of dine:', len(dine))

    # request.session['user_id'] = 1
    return render(request, 'manager/display.html', {'date': date, 'place': place, 'restaurant': restaurant, 'destination': destination})

def place(request, pid):
    print('place page:')
    # place = Place.objects.get(pid = pid)
    place = Place.objects.raw('SELECT * FROM place WHERE pid=%s',[pid])[0]
    # events = Event.objects.filter(pid = pid).order_by('start_date')
    events = Event.objects.raw('SELECT * FROM event WHERE pid=%s', [pid])
    print(place.p_name,' event:', len(events))
    # create visit
    if request.method == 'POST':
        date = request.POST['date']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']
        # user = User.objects.get(uid = request.session['user_id'])
        user = User.objects.raw('SELECT * FROM user WHERE uid = %s', [request.session['user_id']])[0]

        # visit_instance = Visit.objects.create(uid = user, pid = place, date = date, start_time = start_time, end_time = end_time)
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO Visit (uid, pid, date, start_time, end_time) VALUES (%s, %s, %s, %s, %s)", [user.uid ,place.pid, date, start_time, end_time])
  
        return render(request, 'manager/place.html',
        {'place': place, 'events': events, 'date': date, 'start_time': start_time, 'end_time': end_time})

    return render(request, 'manager/place.html', {'place': place, 'events': events, 'pid': pid})



def recommend(request):
    # Treasure restaurants you may not find yet
    #rec_list = NRestaurant.objects.values('categories').annotate(avgcount=Avg('review_count')).filter(review_count__lte=F('avgcount'),stars__gte=4).values('categories','r_name','r_address')[:15]
    
    rec_list = {}
    with connection.cursor() as cursor:
         cursor.execute("SELECT r.r_name FROM n_restaurant r NATURAL JOIN (SELECT categories, avg(review_count) as count FROM n_restaurant GROUP BY categories) AS t WHERE r.stars >= 4 AND r.review_count <= t.count LIMIT 8")
         tup = cursor.fetchall()
         rec_list = [t[0] for t in tup]
    

    # Cities that hold lots of events recently
    # queryset = Place.objects.select_related('event', 'city').values('cid').annotate(c=Count('event')).order_by('-c')[:15]
    # cnames = City.objects.filter(cid__in=[queryset[i]['cid'] for i in range(len(queryset))]).values('c_name')
   
    with connection.cursor() as acursor: 
         acursor.execute("SELECT c.c_name FROM city c, (SELECT p.cid as cid, COUNT(e.eid) as amount FROM event e NATURAL JOIN place p GROUP BY p.cid ORDER BY amount DESC) as t WHERE c.cid=t.cid LIMIT 8")
         tup2 = acursor.fetchall()
         cnames = [t[0] for t in tup2]

    return render(request, 'timeline/recommend.html', {'rec_list': rec_list, 'cnames': cnames})



def restaurant(request, rid):
    print('restaurant page:')
    # restaurant = NRestaurant.objects.get(id = rid)
    restaurant = NRestaurant.objects.raw('SELECT * FROM n_restaurant WHERE id = %s', [rid])[0]

    # create dine
    if request.method == 'POST':
        date = request.POST['date']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']
        # user = User.objects.get(uid = request.session['user_id'])
        user = User.objects.raw('SELECT * FROM user WHERE uid = %s', [request.session['user_id']])[0]
        # Dine_instance = Dine.objects.create(uid = user, rid = restaurant, date = date, start_time = start_time, end_time = end_time)
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO Dine (uid, rid, date, start_time, end_time) VALUES (%s, %s, %s, %s, %s)", [user.uid, restaurant.id, date, start_time, end_time])
  
        return render(request, 'manager/restaurant.html', 
        {'restaurant': restaurant, 'date': date, 'start_time': start_time, 'end_time': end_time})
    # display restaurant
    return render(request, 'manager/restaurant.html', {'restaurant': restaurant})

def delete_visit(request, vid):
    # print(request)

    #Visit.objects.filter(vid=vid).delete()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM visit WHERE vid=%s", [vid])
        #cursor.fetchall()
    return render(request, 'manager/index.html')

def edit_visit(request,vid):
    visit = Visit.objects.filter(vid=vid).first()
    with connection.cursor() as cursor:
        cursor.execute("select p_name,location from place where pid = (select pid from visit where vid = %s)", [vid])
        rst = cursor.fetchone()
    place = {}
    place['p_name'] = rst[0]
    place['location'] = rst[1]
    
    if request.method == 'POST':
        date = request.POST['date']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']
        public = 1 if 'public' in request.POST else 0
        new_review = request.POST['review']
        review = new_review if len(new_review) else visit.review
        stars = request.POST['stars'] if 'stars' in request.POST else None
        stars = stars if stars else visit.v_rate
        trans = request.POST['trans']
        spend = request.POST['spend']

        

        #user = User.objects.get(uid = request.session['user_id'])
        #Visit.objects.filter(vid=vid).update( date = date, start_time = start_time, end_time = end_time)
        with connection.cursor() as cursor:
            cursor.execute("UPDATE visit SET date = %s , start_time=%s , end_time=%s, public = %s, review = %s, v_rate=%s,transport_fee=%s, v_cost=%s  WHERE vid = %s", 
            [date, start_time, end_time, public, review, stars,trans,spend, vid])
            cursor.fetchone()
    return render(request, 'manager/edit_visit.html', {'place':place, 'visit':visit})

def delete_dine(request, did):
    # print(request)

    #Dine.objects.filter(did=did).delete()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM dine WHERE did=%s", [did])

    return render(request, 'manager/index.html')

def edit_dine(request,did):
    dine = Dine.objects.filter(did=did).first()
    with connection.cursor() as cursor:
        cursor.execute("select r_name,r_address,categories,stars,review_count,hours from n_restaurant where id = (select rid from dine where did = %s)", [did])
        rst = cursor.fetchone()
    restaurant = {}
    restaurant['r_name'] = rst[0]
    restaurant['r_address'] = rst[1]
    restaurant['categories'] = rst[2]
    restaurant['stars'] = rst[3]
    restaurant['review_count'] = rst[4]
    restaurant['hours'] = rst[5]


    if request.method == 'POST':
        date = request.POST['date']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']
        public = 1 if 'public' in request.POST else 0
        new_review = request.POST['review']
        review = new_review if len(new_review) else dine.review
        new_order = request.POST['order']
        order = new_order if len(new_order) else dine.orders
        stars = int(request.POST['stars']) if 'stars' in request.POST else None
        stars = stars if stars else dine.d_rate
        spend = request.POST['spend']
        # print('Stars:',stars)
        # Dine.objects.filter(did=did).update( date = date, start_time = start_time, end_time = end_time)
        new_rate = restaurant['stars']*restaurant['review_count']
        # print(new_rate)
        if 'stars' in request.POST:
            new_rate += int(request.POST['stars'])
            if dine.d_rate:
                new_rate -= dine.d_rate
            else:
                restaurant['review_count'] +=1
        new_rate /= restaurant['review_count']
        
        with connection.cursor() as cursor:
            cursor.execute("UPDATE dine SET date = %s , start_time=%s , end_time=%s, public = %s, review = %s, orders = %s, d_rate=%s, d_cost = %s WHERE did = %s", 
            [date, start_time, end_time, public,review, order, stars, spend,did])
            cursor.fetchone()
            cursor.execute("UPDATE n_restaurant SET stars=%s, review_count=%s WHERE id = (select rid from dine where did = %s)", 
            [new_rate, restaurant['review_count'], did])
            cursor.fetchone()
        return render(request, 'manager/index.html')

    return render(request, 'manager/edit_dine.html', {'restaurant': restaurant})

def myplan(request, mode):
    plans = {}
    today = datetime.date.today()
    with connection.cursor() as cursor:
        cursor.execute("(SELECT DISTINCT date FROM visit NATURAL JOIN place WHERE uid = %s) UNION (SELECT DISTINCT date FROM dine NATURAL JOIN n_restaurant WHERE uid = %s) ORDER BY date", [request.session['user_id'], request.session['user_id']])
        date = cursor.fetchall()
        # print("Dates:", date)

        for da in date:
            if mode=='upcoming' and da[0]<today:
                continue
            cursor.execute("SELECT start_time, end_time, p_name, location, vid FROM visit NATURAL JOIN place WHERE date = %s AND uid = %s", [da, request.session['user_id']])
            visit = cursor.fetchall()
            visit = [[v[0], v[1], v[2], v[3], v[4], 1] for v in visit]

            cursor.execute("SELECT start_time, end_time, r_name, r_address, did FROM dine JOIN n_restaurant on dine.rid = n_restaurant.id WHERE date = %s AND uid = %s", [da, request.session['user_id']])
            dine = cursor.fetchall()
            dine = [[d[0], d[1], d[2], d[3], d[4], 0] for d in dine]

            destination = sorted(visit + dine)
            plans[da[0]] = destination
    # print('Plans:', plans)
    # for d in date:
    #     print(d)
    #     print(plans[d[0]])
    return render(request, 'manager/myplan.html', {'plans': plans, 'mode': 1 if mode=='all' else 0})

def add_event(request, pid):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO event (title, start_date, pid) VALUES (%s, %s, %s)",
            [request.POST['title'],request.POST['date'], pid])
        print('add successful!')
        return HttpResponseRedirect('/manager/search/place/%s/' % pid)
    return render(request,'manager/add_event.html')
    
def edit_event(request, eid):
    with connection.cursor() as cursor:
        cursor.execute("select title, start_date, pid from event where eid = %s", [eid])
        rst = cursor.fetchone()
    event = {}
    event['title'] = rst[0]
    event['start_date'] = rst[1]
    event['pid'] = rst[2]

    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("UPDATE event SET title = %s, start_date = %s WHERE eid = %s",
            [request.POST['title'],request.POST['date'],eid])
        event['title'] = request.POST['title']
        event['start_date'] = request.POST['date']

    return render(request,'manager/edit_event.html', {'event': event})   

def delete_event(request, eid):
    with connection.cursor() as cursor:
        cursor.execute("select pid from event where eid = %s", [eid])
        pid = cursor.fetchone()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM event WHERE eid= %s", [eid])
    return HttpResponseRedirect('/manager/search/place/%s/' % pid)
