#from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
from django.shortcuts import render
from manager.models import City, Place, NRestaurant, Event
from timeline.models import Visit, Dine
from django.db import connection
import datetime


def index(request):
    print('display page:')
    return render(request, 'community/display.html')


def plan(request):
    plans = {}
    city = City.objects.raw('SELECT * FROM city WHERE c_name=%s',[request.GET['city']])[0]
    cid = city.cid
    c_name = city.c_name
    print(c_name)
    with connection.cursor() as cursor:
        cursor.execute("(SELECT DISTINCT date FROM visit NATURAL JOIN place ) UNION (SELECT DISTINCT date FROM dine NATURAL JOIN n_restaurant) ORDER BY date")
        date = cursor.fetchall()
        cursor.execute("(SELECT DISTINCT uid FROM visit)UNION (SELECT DISTINCT uid FROM dine)")
        uids = cursor.fetchall()
        #for u in uids:
            #print(u[0])
        #print(type(uids))

        for da in date:
                cursor.execute("SELECT start_time, end_time, p_name, location, vid, uid FROM visit NATURAL JOIN place WHERE date = %s AND cid = %s ", [da, cid])
                visit = cursor.fetchall()
                visit = [[v[0], v[1], v[2], v[3], v[4], v[5]] for v in visit]

                cursor.execute("SELECT start_time, end_time, r_name, r_address, did, uid FROM dine JOIN n_restaurant on dine.rid = n_restaurant.id WHERE date = %s AND cid = %s", [da, cid])
                dine = cursor.fetchall()
                dine = [[d[0], d[1], d[2], d[3], d[4], d[5]] for d in dine]

                destination = sorted(visit + dine)
                plans[da[0]] = destination
    return render(request, 'community/display.html', {'city': c_name, 'plans': plans})


