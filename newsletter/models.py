from django.db import models

# Create your models here.
class Newsletter(models.Model):
    email = models.EmailField(max_length=254)
    status = models.BooleanField(default=True)
    time_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email