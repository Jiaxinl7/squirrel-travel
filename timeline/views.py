# Create your views here.
from django.http import HttpResponse
from django.db.models.aggregates import Count
from django.shortcuts import render
from manager.models import City, Place, NRestaurant, Event
from .models import Visit, Dine
from user.models import User
from django.db import models, connection
from django.db.models.aggregates import Avg, Count



def profile(request, uid):
    
    # Count the places (the user v.s avg(all users)) have been to 
    with connection.cursor() as cursor:
         cursor.execute('SELECT COUNT(*) FROM visit WHERE uid = %s', [request.session['user_id']])
         uvcnt = cursor.fetchone()
    with connection.cursor() as cursor:
         cursor.execute('SELECT ROUND(avg(per),2) FROM (SELECT uid, COUNT(vid) as per FROM visit GROUP BY uid) as t')
         avcnt = cursor.fetchone()

    # The competence of the user(places)
    with connection.cursor() as cursor:
         cursor.execute('SELECT DISTINCT q.arank \
                        FROM (SELECT uid, CUME_DIST() OVER (ORDER BY ud_cnt) AS arank \
                              FROM (SELECT uid,COUNT(pid) OVER (PARTITION BY uid) AS ud_cnt FROM visit) as t) as q\
                              WHERE q.uid=%s', [request.session['user_id']])
         rancp = cursor.fetchone()

    # Count the restaurants (the user v.s avg(all users)) have dined 
    with connection.cursor() as cursor:
         cursor.execute('SELECT COUNT(did) FROM dine WHERE uid = %s', [request.session['user_id']])
         udcnt = cursor.fetchone()
    with connection.cursor() as cursor:
         cursor.execute('SELECT ROUND(avg(per),2) FROM (SELECT uid, COUNT(did) as per FROM dine GROUP BY uid) as t')
         adcnt = cursor.fetchone()

    # The competence of the user(restaurants)
    with connection.cursor() as cursor:
         cursor.execute('SELECT DISTINCT q.arank \
                        FROM (SELECT uid, CUME_DIST() OVER (ORDER BY ud_cnt) AS arank \
                              FROM (SELECT uid,COUNT(did) OVER (PARTITION BY uid) AS ud_cnt FROM dine) as t) as q\
                              WHERE q.uid=%s', [request.session['user_id']])
         rancr = cursor.fetchone()

    # Radar Plot(Which categories does the user go to)
    menu = ["Arts", "Restaurant", "Shopping", "Health", "Sport", "Service"]
    plans = []
    for m in menu:
       with connection.cursor() as cursor:
            cursor.execute('SELECT COUNT(d.did) \
                            FROM n_restaurant r JOIN dine d ON r.id=d.rid \
                            WHERE categories LIKE %s AND d.uid = %s\
                            GROUP BY d.uid', ['%'+m+'%', request.session['user_id']])                
            temp = cursor.fetchone()
            temptt = temp[0] if temp is not None else 0
            plans.append(temptt)
            s = int(0 if sum(plans) is None else sum(plans))
            plans = [round(e/s, 2) for e in plans] if s != 0 else [0]*6


    # Expenses user v.s all 
    with connection.cursor() as cursor:
         cursor.execute('SELECT ifnull(SUM(v_cost),0) FROM visit WHERE uid = %s', [request.session['user_id']])
         uvspend = cursor.fetchone()[0]
    with connection.cursor() as cursor:
         cursor.execute('SELECT ROUND(AVG(per),2) FROM (SELECT uid, SUM(v_cost) as per FROM visit GROUP BY uid) as t')
         avspend = cursor.fetchone()[0]
    uv_type = 1 if uvspend > avspend else 0

    with connection.cursor() as cursor:
         cursor.execute('SELECT ifnull(SUM(d_cost),0) FROM dine WHERE uid = %s', [request.session['user_id']])
         udspend = cursor.fetchone()[0]
    with connection.cursor() as cursor:
         cursor.execute('SELECT ROUND(AVG(per),2) FROM (SELECT uid, SUM(d_cost) as per FROM dine GROUP BY uid) as t')
         adspend = cursor.fetchone()[0]
    ud_type = 1 if udspend > adspend else 0
  

    # Kind Grader or...
    with connection.cursor() as cursor:
         cursor.execute('SELECT ifnull(ROUND(avg(r.stars),2),0), ifnull(ROUND(avg(d.d_rate),2),0)\
                         FROM n_restaurant r JOIN dine d ON r.id=d.rid\
                        WHERE r.id IN (SELECT rid\
			                            FROM dine\
			                            WHERE uid=%s)', [request.session['user_id']])
         abox = cursor.fetchone()
    g_type = 0 if abox[0]==0 else 1 if abox[1]>abox[0] else 2

    return render(request, 'timeline/profile.html', {'uvcnt': uvcnt})

