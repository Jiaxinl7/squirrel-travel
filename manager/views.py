from django.db.models.aggregates import Count
from django.shortcuts import render
from .models import City, Place, NRestaurant, Event
from timeline.models import Visit, Dine
from user.models import User
from django.db import models, connection
from django.db.models.aggregates import Avg, Count


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
        cursor.execute("SELECT start_time, end_time, p_name, location, vid FROM visit NATURAL JOIN place WHERE date = %s", [date])
        visit = cursor.fetchall()
    visit = [[v[0], v[1], v[2], v[3], v[4], 1] for v in visit]
    print('len of visit:', len(visit))

    # dine = Dine.objects.select_related('rid').filter(date=date)
    with connection.cursor() as cursor:
        cursor.execute("SELECT start_time, end_time, r_name, r_address, did FROM dine JOIN n_restaurant on dine.rid = n_restaurant.id WHERE date = %s", [date])
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

    return render(request, 'manager/place.html', {'place': place, 'events': events})



def recommend(request):
    # Treasure restaurants you may not find yet
    #rec_list = NRestaurant.objects.values('categories').annotate(avgcount=Avg('review_count')).filter(review_count__lte=F('avgcount'),stars__gte=4).values('categories','r_name','r_address')[:15]
    
    with connection.cursor() as cursor:
         cursor.execute("SELECT r.r_name FROM n_restaurant r NATURAL JOIN (SELECT categories, avg(review_count) as count FROM n_restaurant GROUP BY categories) AS t WHERE r.stars >= 4 AND r.review_count <= t.count LIMIT 15")
         rec_list = cursor.fetchall()


    # Cities that hold lots of events recently
    # queryset = Place.objects.select_related('event', 'city').values('cid').annotate(c=Count('event')).order_by('-c')[:15]
    # cnames = City.objects.filter(cid__in=[queryset[i]['cid'] for i in range(len(queryset))]).values('c_name')
   
    with connection.cursor() as acursor: 
         acursor.execute("SELECT c.c_name FROM city c, (SELECT p.cid as cid, COUNT(e.eid) as amount FROM event e NATURAL JOIN place p GROUP BY p.cid ORDER BY amount DESC) as t WHERE c.cid=t.cid LIMIT 15")
         cnames = acursor.fetchall()

    return render(request, 'manager/advancedquery.html', {'rec_list': rec_list, 'cnames': cnames})



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
    if request.method == 'POST':
        date = request.POST['date']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']
        #user = User.objects.get(uid = request.session['user_id'])
        #Visit.objects.filter(vid=vid).update( date = date, start_time = start_time, end_time = end_time)
        with connection.cursor() as cursor:
            cursor.execute("UPDATE visit SET date = %s , start_time=%s , end_time=%s WHERE vid = %s", [date, start_time, end_time, vid])
            cursor.fetchone()
        return render(request, 'manager/index.html')
    return render(request, 'manager/edit_visit.html')

def delete_dine(request, did):
    # print(request)

    #Dine.objects.filter(did=did).delete()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM dine WHERE did=%s", [did])

    return render(request, 'manager/index.html')

def edit_dine(request,did):
    dine = Dine.objects.filter(did=did).first()
    if request.method == 'POST':
        date = request.POST['date']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']
        # Dine.objects.filter(did=did).update( date = date, start_time = start_time, end_time = end_time)
        with connection.cursor() as cursor:
            cursor.execute("UPDATE dine SET date = %s , start_time=%s , end_time=%s WHERE did = %s", [date, start_time, end_time, did])
            cursor.fetchone()
        return render(request, 'manager/index.html')
    return render(request, 'manager/edit_dine.html')