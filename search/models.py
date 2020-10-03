from django.db import models
from django.contrib.auth.models import User

class SearchLog(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    query = models.CharField(max_length=3000)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.PROTECT)
    ip_address = models.CharField(max_length=1000)
    device_type = models.CharField(max_length=1000)
    browser_type = models.CharField(max_length=1000)
    browser_version = models.CharField(max_length=1000)
    os_type = models.CharField(max_length=1000)
    os_version = models.CharField(max_length=1000)