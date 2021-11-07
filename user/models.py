from django.db import models

# Create your models here.
class User(models.Model):
    uid = models.AutoField(primary_key=True)
    u_name = models.CharField(max_length=45, blank=True, null=True)
    password = models.CharField(max_length=45, blank=True, null=True)
    email = models.CharField(max_length=45, blank=True, null=True)
    user_type = models.CharField(max_length=45, blank=True, null=True)        

    class Meta:
        db_table = 'user'