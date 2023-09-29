from django.db import models

# Create your models here.
class Sample(models.Model):
    name = models.CharField(max_length=255)
    sample_image = models.ImageField(upload_to='sample_images/')  # 'item_images/' is the upload directory, you can customize it.

    def __str__(self):
        return self.name