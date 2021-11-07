# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Visit(models.Model):
    vid = models.IntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    v_cost = models.FloatField(blank=True, null=True)
    transport_fee = models.FloatField(blank=True, null=True)
    review = models.CharField(max_length=255, blank=True, null=True)
    public = models.IntegerField(blank=True, null=True)
    v_rate = models.FloatField(blank=True, null=True)
    uid = models.ForeignKey('User', models.DO_NOTHING, db_column='uid')
    pid = models.ForeignKey('Place', models.DO_NOTHING, db_column='pid')

    class Meta:
        managed = False
        db_table = 'visit'


class Dine(models.Model):
    did = models.IntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    d_cost = models.FloatField(blank=True, null=True)
    review = models.CharField(max_length=255, blank=True, null=True)
    public = models.IntegerField(blank=True, null=True)
    orders = models.CharField(max_length=255, blank=True, null=True)
    d_rate = models.FloatField(blank=True, null=True)
    rid = models.ForeignKey('NRestaurant', models.DO_NOTHING, db_column='rid')
    uid = models.ForeignKey('User', models.DO_NOTHING, db_column='uid')

    class Meta:
        managed = False
        db_table = 'dine'
