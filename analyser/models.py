from django.db import models

# Create your models here.


class Sample(models.Model):
    name = models.CharField(max_length=255)
    # 'item_images/' is the upload directory, you can customize it.
    sample_image = models.ImageField(upload_to='samples/')
    analysis_results = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.name
