from django.db import models

# Create your models here.

class UserRecord(models.Model):
    name = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    C = models.FloatField()
    E = models.FloatField()
    A = models.FloatField()
    N = models.FloatField()
    O = models.FloatField()

    def __str__(self):
        return "Record for {}".format(self.name)

