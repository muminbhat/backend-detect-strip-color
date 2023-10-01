from django.db import models
from cloudinary.models import CloudinaryField

# Create your models here.


class Sample(models.Model):
    name = models.CharField(max_length=255)
    # 'item_images/' is the upload directory, you can customize it.
    sample_image = CloudinaryField('sample_image', null=True, blank=True)
    analysis_results = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.name
