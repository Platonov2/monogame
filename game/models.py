from django.db import models

# Create your models here.

class UsersInfo(models.Model):
    name = models.CharField(max_length=32)
    surname=models.CharField(max_length=32)

class  operatingAccuracy(models.Model):
       user=models.ForeignKey(UsersInfo,on_delete=models.CASCADE)
       #Положительное или отрицательное значение после каждого клика
       left_accuracy=models.FloatField()
       middle_accuracy=models.FloatField()
       right_accuracy=models.FloatField()

class state(models.Model):
      user=models.ForeignKey(UsersInfo,on_delete=models.CASCADE)
      previous_stressIndex = models.FloatField()
      after_stressIndex = models.FloatField()
      strart_lf_hf = models.FloatField()
      end_lf_hf = models.FloatField()


class result(models.Model):
    user = models.ForeignKey(UsersInfo, on_delete=models.CASCADE)
    monotony=models.BooleanField()


