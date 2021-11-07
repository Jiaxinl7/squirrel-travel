from django.db import models

# Create your models here.
class City(models.Model):
    c_name = models.CharField(max_length=45, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    population = models.IntegerField(blank=True, null=True)
    cid = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'city'

class Event(models.Model):
    eid = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    pid = models.ForeignKey('Place', models.DO_NOTHING, db_column='pid', blank=True, null=True)

    class Meta:
        db_table = 'event'

class Manage(models.Model):
    uid = models.IntegerField(primary_key=True)
    pid = models.IntegerField()

    class Meta:
        db_table = 'manage'
        unique_together = (('uid', 'pid'),)

class NRestaurant(models.Model):
    cid = models.ForeignKey(City, models.DO_NOTHING, db_column='cid')
    r_address = models.CharField(max_length=255, blank=True, null=True)       
    id = models.CharField(primary_key=True, max_length=45)
    categories = models.TextField(blank=True, null=True)
    r_city = models.CharField(max_length=45, blank=True, null=True)
    hours = models.CharField(max_length=255, blank=True, null=True)
    is_open = models.IntegerField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    r_name = models.CharField(max_length=255, blank=True, null=True)
    review_count = models.IntegerField(blank=True, null=True)
    stars = models.FloatField(blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'n_restaurant'

class Place(models.Model):
    pid = models.IntegerField(primary_key=True)
    p_name = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)        
    cid = models.ForeignKey(City, models.DO_NOTHING, db_column='cid', blank=True, null=True)

    class Meta:
        db_table = 'place'