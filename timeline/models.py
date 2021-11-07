from django.db import models

# Create your models here.
class Visit(models.Model):
    # vid = models.IntegerField(primary_key=True)
    vid = models.AutoField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    v_cost = models.FloatField(blank=True, null=True)
    transport_fee = models.FloatField(blank=True, null=True)
    review = models.CharField(max_length=255, blank=True, null=True)
    public = models.IntegerField(blank=True, null=True)
    v_rate = models.FloatField(blank=True, null=True)
    uid = models.IntegerField()
    pid = models.IntegerField()

    class Meta:
        db_table = 'visit'

class Dine(models.Model):
    # did = models.IntegerField(primary_key=True)
    did = models.AutoField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    d_cost = models.FloatField(blank=True, null=True)
    review = models.CharField(max_length=255, blank=True, null=True)
    public = models.IntegerField(blank=True, null=True)
    orders = models.CharField(max_length=255, blank=True, null=True)
    d_rate = models.FloatField(blank=True, null=True)
    rid = models.IntegerField()
    uid = models.IntegerField()

    class Meta:
        db_table = 'dine'