from django.contrib import admin

# Register your models here.

from game import models
admin.site.register(models.UsersInfo)
admin.site.register(models.operatingAccuracy)
admin.site.register(models.state)
admin.site.register(models.result)
