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
         box1 = cursor.fetchone()
         uvcnt = box1[0] if box1 is not None else 0
 
    with connection.cursor() as cursor:
         cursor.execute('SELECT ROUND(avg(per),2) FROM (SELECT uid, COUNT(vid) as per FROM visit GROUP BY uid) as t')
         box2 = cursor.fetchone()
         avcnt = box2[0] if box2 is not None else 0

    # The competence of the user(places)
    with connection.cursor() as cursor:
         cursor.execute('SELECT DISTINCT q.arank \
                        FROM (SELECT uid, CUME_DIST() OVER (ORDER BY ud_cnt) AS arank \
                              FROM (SELECT uid,COUNT(pid) OVER (PARTITION BY uid) AS ud_cnt FROM visit) as t) as q\
                              WHERE q.uid=%s', [request.session['user_id']])
         box3 = cursor.fetchone()
         rancp = box3[0] if box3 is not None else 0

    # Count the restaurants (the user v.s avg(all users)) have dined 
    with connection.cursor() as cursor:
         cursor.execute('SELECT COUNT(did) FROM dine WHERE uid = %s', [request.session['user_id']])
         box4 = cursor.fetchone()
         udcnt = box4[0] if box4 is not None else 0

    with connection.cursor() as cursor:
         cursor.execute('SELECT ROUND(avg(per),2) FROM (SELECT uid, COUNT(did) as per FROM dine GROUP BY uid) as t')
         box5 = cursor.fetchone()
         adcnt = box5[0] if box5 is not None else 0

    # The competence of the user(restaurants)
    with connection.cursor() as cursor:
         cursor.execute('SELECT DISTINCT q.arank \
                        FROM (SELECT uid, CUME_DIST() OVER (ORDER BY ud_cnt) AS arank \
                              FROM (SELECT uid,COUNT(did) OVER (PARTITION BY uid) AS ud_cnt FROM dine) as t) as q\
                              WHERE q.uid=%s', [request.session['user_id']])
         box6 = cursor.fetchone()
         rancr = box6[0] if box6 is not None else 0   

    # Radar Plot(Which categories does the user go to)
    menu = ["Arts", "Restaurant", "Shopping", "Health", "Sport", "Service"]
    spend = []
    for m in menu:
       with connection.cursor() as cursor:
            cursor.execute('SELECT COUNT(d.did) \
                            FROM n_restaurant r JOIN dine d ON r.id=d.rid \
                            WHERE categories LIKE %s AND d.uid = %s\
                            GROUP BY d.uid', ['%'+m+'%', request.session['user_id']])                
            temp = cursor.fetchone()
            temptt = temp[0] if temp is not None else 0
            spend.append(temptt)
            s = int(0 if sum(spend) is None else sum(spend))
            spend = [round(e/s, 2) for e in spend] if s != 0 else [0]*6


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

    with connection.cursor() as cursor:
         cursor.execute('SELECT u_name FROM user WHERE uid=%s',[request.session['user_id']])
         u = cursor.fetchone()[0]
    return render(request, 'timeline/profile.html', 
                  {'uvcnt': uvcnt, 'avcnt': avcnt, 'rancp': rancp, 'udcnt': udcnt, 'adcnt': adcnt, 
                  'rancr': rancr, 'spend': spend, 'g_type': g_type, 'u':u})


