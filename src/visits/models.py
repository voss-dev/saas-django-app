from django.db import models

# Create your models here.
class PageVisit(models.Model):
    # Hidden primary key column automatically created by Django
    # id = models.AutoField(primary_key=True)

    path = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)